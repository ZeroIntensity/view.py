"""
view.py app implementation

This module contains the `App` class, `new_app`, and `get_app`.

Note that the actual ASGI functionality is stored under the `ViewApp`
extension type, which `App` inherits from.
"""

from __future__ import annotations

import asyncio
import ctypes
import faulthandler
import inspect
import logging
import os
import sys
import warnings
import weakref
from collections.abc import Iterable as CollectionsIterable
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from functools import lru_cache, partial
from io import UnsupportedOperation
from pathlib import Path
from queue import Queue
from threading import Thread
from types import FrameType as Frame
from types import TracebackType as Traceback
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    TextIO,
    TypeVar,
    get_type_hints,
    overload,
)
from urllib.parse import urlencode

import ujson
from rich import print
from rich.traceback import install
from typing_extensions import ParamSpec, TypeAlias

from _view import InvalidStatusError, ViewApp

from .__main__ import welcome
from ._docs import markdown_docs
from ._loader import finalize, load_fs, load_patterns, load_simple
from ._logging import (
    LOGS,
    Hijack,
    Internal,
    Service,
    enter_server,
    exit_server,
    format_warnings,
)
from ._parsers import supply_parsers
from ._util import needs_dep
from .config import Config, load_config
from .exceptions import (
    BadEnvironmentError,
    InvalidCustomLoaderError,
    ViewError,
    ViewInternalError,
    WebSocketDisconnectError,
)
from .response import HTML
from .routing import Path as _RouteDeco
from .routing import (
    Route,
    RouteInput,
    RouteOrCallable,
    RouteOrWebsocket,
    V,
    _NoDefault,
    _NoDefaultType,
)
from .routing import body as body_impl
from .routing import context as context_impl
from .routing import delete, get, options, patch, post, put
from .routing import query as query_impl
from .routing import route as route_impl
from .routing import websocket
from .templates import _CurrentFrame, _CurrentFrameType, markdown, template
from .typing import Callback, DocsType, ErrorStatusCode, StrMethod, TemplateEngine
from .util import enable_debug
from .ws import WebSocket

ReactPyComponent: TypeAlias = Any

get_type_hints = lru_cache(get_type_hints)  # type: ignore

__all__ = "App", "new_app", "get_app", "HTTPError", "ERROR_CODES"

S = TypeVar("S", int, str, dict, bool)
A = TypeVar("A")
T = TypeVar("T")
P = ParamSpec("P")

_ROUTES_WARN_MSG = "routes argument should only be passed when load strategy is manual"
_ConfigSpecified = None

B = TypeVar("B", bound=BaseException)
CustomLoader: TypeAlias = Callable[["App", Path], Iterable[Route]]

ERROR_CODES: tuple[ErrorStatusCode, ...] = (
    400,
    401,
    402,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    421,
    422,
    423,
    424,
    425,
    426,
    428,
    429,
    431,
    451,
    500,
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    510,
    511,
)


class TestingResponse:
    def __init__(
        self,
        message: str | None,
        headers: dict[str, str],
        status: int,
        content: bytes,
    ) -> None:
        self._message = message
        self.headers = headers
        self.status = status
        self.content = content

    @property
    def message(self) -> str:
        if self._message is None:
            raise RuntimeError("cannot decode content into string")

        return self._message


def _format_qs(query: dict[str, Any]) -> dict[str, Any]:
    query_str = {}

    for k, v in query.items():
        if isinstance(v, (dict, list)):
            if isinstance(v, dict):
                query_str[k] = ujson.dumps(_format_qs(v))
            else:
                query_str[k] = ujson.dumps(v)
        else:
            query_str[k] = v

    return query_str


async def _to_thread(func: Callable[[], T]) -> T:
    if hasattr(asyncio, "to_thread"):
        return await asyncio.to_thread(func)
    else:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func)


class VirtualWebSocket:
    def __init__(self) -> None:
        self.recv_queue = Queue()
        self.send_queue = Queue()
        self.recv_queue.put_nowait({"type": "websocket.connect"})

    async def close(self):
        self.recv_queue.put_nowait({"type": "websocket.disconnect"})

    async def _server_receive(self):
        return await _to_thread(self.recv_queue.get)

    async def _server_send(self, data: dict):
        self.send_queue.put_nowait(data)

    async def send(self, message: str) -> None:
        self.recv_queue.put_nowait({"type": "websocket.receive", "text": message})

    async def receive(self) -> str:
        data = await _to_thread(self.send_queue.get)
        msg = data.get("text") or data.get("bytes")

        if not msg:
            reason = data.get("reason")
            if reason:
                raise RuntimeError(reason)
            raise ViewInternalError(f"{data!r} has no text or bytes key")

        return msg

    async def handshake(self) -> None:
        assert (await _to_thread(self.send_queue.get))["type"] == "websocket.accept"


class TestingContext:
    def __init__(
        self,
        app: Callable[[Any, Any, Any], Any],
    ) -> None:
        self.app = app
        self._lifespan: asyncio.Queue[str] = asyncio.Queue()
        self._lifespan.put_nowait("lifespan.startup")

    async def start(self) -> None:
        async def receive():
            return await self._lifespan.get()

        async def send(_: dict[str, Any]):
            pass

        await self.app({"type": "lifespan"}, receive, send)

    async def stop(self) -> None:
        await self._lifespan.put("lifespan.shutdown")

    def _gen_headers(self, headers: dict[str, str]) -> list[tuple[bytes, bytes]]:
        return [
            (key.encode(), value.encode()) for key, value in (headers or {}).items()
        ]

    def _truncate(self, route: str) -> str:
        return route[: route.find("?")] if "?" in route else route

    async def _request(
        self,
        method: str,
        route: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TestingResponse:
        body_q: asyncio.Queue[bytes] = asyncio.Queue()
        start: asyncio.Queue[tuple[dict[str, str], int]] = asyncio.Queue()

        async def receive():
            return {
                "body": ujson.dumps(body).encode(),
                "more_body": False,
                "type": "http.request",
            }

        async def send(obj: dict[str, Any]):
            if obj["type"] == "http.response.start":
                await start.put(
                    (
                        {k.decode(): v.decode() for k, v in obj["headers"]},
                        obj["status"],
                    )
                )
            elif obj["type"] == "http.response.body":
                assert isinstance(obj["body"], bytes)
                await body_q.put(obj["body"])
            else:
                raise ViewInternalError(f"bad type: {obj['type']}")

        truncated_route = self._truncate(route)
        query_str = _format_qs(query or {})
        headers_list = self._gen_headers(headers or {})

        await self.app(
            {
                "type": "http",
                "path": truncated_route,
                "query_string": (
                    urlencode(query_str).encode() if query else b""
                ),  # noqa
                "headers": headers_list,
                "method": method,
                "http_version": "view_test",
                "scheme": "http",
                "client": None,
                "server": None,
            },
            receive,
            send,
        )

        res_headers, status = await start.get()
        body_b = await body_q.get()

        try:
            body_s: str | None = body_b.decode()
        except UnicodeError:
            body_s = None

        return TestingResponse(body_s, res_headers, status, body_b)

    async def get(
        self,
        route: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TestingResponse:
        return await self._request(
            "GET",
            route,
            body=body,
            query=query,
            headers=headers,
        )

    async def post(
        self,
        route: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TestingResponse:
        return await self._request(
            "POST",
            route,
            body=body,
            query=query,
            headers=headers,
        )

    async def put(
        self,
        route: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TestingResponse:
        return await self._request(
            "PUT",
            route,
            body=body,
            query=query,
            headers=headers,
        )

    async def patch(
        self,
        route: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TestingResponse:
        return await self._request(
            "PATCH",
            route,
            body=body,
            query=query,
            headers=headers,
        )

    async def delete(
        self,
        route: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TestingResponse:
        return await self._request(
            "DELETE",
            route,
            body=body,
            query=query,
            headers=headers,
        )

    async def options(
        self,
        route: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> TestingResponse:
        return await self._request(
            "OPTIONS",
            route,
            body=body,
            query=query,
            headers=headers,
        )

    @asynccontextmanager
    async def websocket(
        self,
        route: str,
        *,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> AsyncIterator[VirtualWebSocket]:
        query_str = _format_qs(query or {})
        headers_list = self._gen_headers(headers or {})
        truncated_route = self._truncate(route)

        socket = VirtualWebSocket()

        def _wrapper():
            loop = asyncio.new_event_loop()
            loop.run_until_complete(
                self.app(
                    {
                        "type": "websocket",
                        "path": truncated_route,
                        "query_string": (
                            urlencode(query_str).encode() if query else b""
                        ),  # noqa
                        "headers": headers_list,
                    },
                    socket._server_receive,
                    socket._server_send,
                )
            )

        Thread(target=_wrapper).start()

        await socket.handshake()
        try:
            yield socket
        finally:
            await socket.close()


@dataclass
class InputDoc(Generic[T]):
    desc: str
    type: tuple[type[T], ...]
    default: T | _NoDefaultType


@dataclass
class RouteDoc:
    desc: str
    body: dict[str, InputDoc]
    query: dict[str, InputDoc]


_LEVELS = dict((v, k) for k, v in LOGS.items())


class HTTPError(BaseException):
    """
    Base class to act as a transport for raising HTTP errors.
    """

    def __init__(
        self, status: ErrorStatusCode = 400, message: str | None = None
    ) -> None:
        """
        Args:
            status: The status code for the resulting response.
            message: The (optional) message to send back to the client. If none, uses the default error message (e.g. `Bad Request` for status `400`).
        """
        if status not in ERROR_CODES:
            raise InvalidStatusError("status code can only be a client or server error")

        self.status = status
        self.message = message


WS_CODES = (1000,)


class WSError(BaseException):
    """
    Base class to act as a transport for raising WebSocket errors.
    """

    def __init__(self, status: int = 1000, message: str | None = None) -> None:
        """
        Args:
            status: The status code for the resulting response.
            message: The (optional) message to send back to the client. If none, uses the default error message.
        """
        if status not in WS_CODES:
            raise InvalidStatusError(f"invalid websocket close code: {status}")

        self.status = status
        self.message = message


_DefinedByConfig = None


class App(ViewApp):
    """
    Main view.py app object.

    You likely don't want to instantiate this class yourself, and should call `new_app()` instead.
    The constructor of this class should be considered unstable - although, it will probably not change all that much.
    """

    def __init__(self, config: Config) -> None:
        supply_parsers(self)
        self.config = config
        """Configuration object."""

        self._set_dev_state(config.dev)
        self._manual_routes: list[Route] = []
        self.loaded: bool = False
        """Whether load() has been called at least once."""
        self.running = False
        """Whether the app is running."""
        self._docs: DocsType = {}
        self.loaded_routes: list[Route] = []
        """Routes loaded into the app."""
        self.templaters: dict[str, Any] = {}
        """Dictionary containing template engine instances."""
        self._reactive_sessions: dict[str, ReactPyComponent] = {}
        self._register_error(HTTPError)
        self._user_loader: CustomLoader | None = None
        self._run_called = False

        os.environ.update({k: str(v) for k, v in config.env.items()})

        Service.log.setLevel(
            config.log.level
            if not isinstance(config.log.level, str)
            else config.log.level.upper()
        )

        if config.dev:
            if os.environ.get("VIEW_PROD") is not None:
                Service.warning("VIEW_PROD is set but dev is set to true")

            format_warnings()
            weakref.finalize(self, self._finalize)

            if config.log.pretty_tracebacks and (not config.log.fancy):
                install(show_locals=True)

            rich_handler = sys.excepthook

            def _hook(tp: type[B], value: B, traceback: Traceback) -> None:
                rich_handler(tp, value, traceback)
                os.environ["_VIEW_CANCEL_FINALIZERS"] = "1"

                if isinstance(value, ViewError):
                    if value.hint:
                        print(value.hint)

                if isinstance(value, ViewInternalError):
                    print("[bold dim red]This is an internal error, not your fault![/]")
                    print(
                        "[bold dim red]Please report this at https://github.com/ZeroIntensity/view.py/issues[/]"
                    )

            sys.excepthook = _hook  # type: ignore
            with suppress(UnsupportedOperation):
                faulthandler.enable()
        else:
            os.environ["VIEW_PROD"] = "1"

        if config.log.level == "debug":
            enable_debug()

        self.running = False

    def _finalize(self) -> None:
        if os.environ.get("_VIEW_CANCEL_FINALIZERS"):
            return

        if self.loaded:
            return

        if not self._run_called:
            warnings.warn("load() was never called (did you forget to start the app?)")
            split = self.config.app.app_path.split(":", maxsplit=1)

            if len(split) != 2:
                return
        else:
            warnings.warn(
                "run() was called, but the app never started. pass force=True to run() to fix this"
            )

    def _push_route(self, route: Route) -> None:
        if route in self._manual_routes:
            return

        self._manual_routes.append(route)

    def route(
        self,
        path_or_route: str | None | RouteOrCallable[P] = None,
        doc: str | None = None,
        *,
        cache_rate: int = -1,
        methods: Iterable[StrMethod] | None = None,
        steps: Iterable[str] | None = None,
        parallel_build: bool | None = _DefinedByConfig,
    ) -> _RouteDeco[P]:
        """
        Add a route that can be called with any method (or only specific methods).

        Args:
            path_or_route: The path to this route, or the route itself.
            doc: The description of the route to be used in documentation.
            cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.
            methods: Methods that can be used to access this route. If this is `None`, then all methods are allowed.

        Example:
            ```py
            from view import route

            @route("/", methods=("GET", "POST"))
            async def index():
                return "Hello, view.py!"
            ```
        """

        def inner(r: RouteOrCallable[P]) -> Route[P]:
            new_r = route_impl(
                path_or_route,
                doc,
                cache_rate=cache_rate,
                methods=methods,
                steps=steps,
                parallel_build=parallel_build,
            )(r)
            self._push_route(new_r)
            return new_r

        return inner

    def custom_loader(self, loader: CustomLoader):
        self._user_loader = loader

    def _method_wrapper(
        self,
        path: str,
        doc: str | None,
        cache_rate: int,
        target: Callable[..., Any],
        steps: Iterable[str] | None,
        parallel_build: bool | None,
        # i dont really feel like typing this properly
    ) -> _RouteDeco[P]:
        def inner(route: RouteOrCallable[P]) -> Route[P]:
            new_route = target(
                path,
                doc,
                cache_rate=cache_rate,
                steps=steps,
                parallel_build=parallel_build,
            )(route)
            self._push_route(new_route)
            return new_route

        return inner

    def websocket(
        self,
        path: str,
        doc: str | None = None,
    ) -> Callable[[RouteOrWebsocket[P]], Route[P]]:
        def inner(route: RouteOrWebsocket[P]) -> Route[P]:
            new_route = websocket(path, doc)(route)
            self._push_route(new_route)
            return new_route

        return inner

    def get(
        self,
        path: str,
        doc: str | None = None,
        *,
        cache_rate: int = -1,
        steps: Iterable[str] | None = None,
        parallel_build: bool | None = _DefinedByConfig,
    ) -> _RouteDeco[P]:
        """
        Add a GET route.

        Args:
            path: The path to this route.
            doc: The description of the route to be used in documentation.
            cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

        Example:
            ```py
            from view import new_app

            app = new_app()

            @app.get("/")
            async def index():
                return "Hello, view.py!"

            app.run()
            ```
        """
        return self._method_wrapper(path, doc, cache_rate, get, steps, parallel_build)

    def post(
        self,
        path: str,
        doc: str | None = None,
        *,
        cache_rate: int = -1,
        steps: Iterable[str] | None = None,
        parallel_build: bool | None = _DefinedByConfig,
    ) -> _RouteDeco[P]:
        """
        Add a POST route.

        Args:
            path: The path to this route.
            doc: The description of the route to be used in documentation.
            cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

        Example:
            ```py
            from view import new_app

            app = new_app()

            @app.post("/")
            async def index():
                return "Hello, view.py!"

            app.run()
            ```
        """
        return self._method_wrapper(
            path,
            doc,
            cache_rate,
            post,
            steps,
            parallel_build,
        )

    def delete(
        self,
        path: str,
        doc: str | None = None,
        *,
        cache_rate: int = -1,
        steps: Iterable[str] | None = None,
        parallel_build: bool | None = _DefinedByConfig,
    ) -> _RouteDeco[P]:
        """
        Add a DELETE route.

        Args:
            path: The path to this route.
            doc: The description of the route to be used in documentation.
            cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

        Example:
            ```py
            from view import new_app

            app = new_app()

            @app.delete("/")
            async def index():
                return "Hello, view.py!"

            app.run()
            ```
        """
        return self._method_wrapper(
            path,
            doc,
            cache_rate,
            delete,
            steps,
            parallel_build,
        )

    def patch(
        self,
        path: str,
        doc: str | None = None,
        *,
        cache_rate: int = -1,
        steps: Iterable[str] | None = None,
        parallel_build: bool | None = _DefinedByConfig,
    ) -> _RouteDeco[P]:
        """
        Add a PATCH route.

        Args:
            path: The path to this route.
            doc: The description of the route to be used in documentation.
            cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

        Example:
            ```py
            from view import new_app

            app = new_app()

            @app.patch("/")
            async def index():
                return "Hello, view.py!"

            app.run()
            ```
        """
        return self._method_wrapper(
            path,
            doc,
            cache_rate,
            patch,
            steps,
            parallel_build,
        )

    def put(
        self,
        path: str,
        doc: str | None = None,
        *,
        cache_rate: int = -1,
        steps: Iterable[str] | None = None,
        parallel_build: bool | None = _DefinedByConfig,
    ) -> _RouteDeco[P]:
        """
        Add a PUT route.

        Args:
            path: The path to this route.
            doc: The description of the route to be used in documentation.
            cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

        Example:
            ```py
            from view import new_app

            app = new_app()

            @app.put("/")
            async def index():
                return "Hello, view.py!"

            app.run()
            ```
        """
        return self._method_wrapper(path, doc, cache_rate, put, steps, parallel_build)

    def options(
        self,
        path: str,
        doc: str | None = None,
        *,
        cache_rate: int = -1,
        steps: Iterable[str] | None = None,
        parallel_build: bool | None = _DefinedByConfig,
    ) -> _RouteDeco[P]:
        """
        Add an OPTIONS route.

        Args:
            path: The path to this route.
            doc: The description of the route to be used in documentation.
            cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

        Example:
            ```py
            from view import new_app

            app = new_app()

            @app.options("/")
            async def index():
                return "Hello, view.py!"

            app.run()
            ```
        """
        return self._method_wrapper(
            path, doc, cache_rate, options, steps, parallel_build
        )

    def query(
        self,
        name: str,
        *tps: type[V],
        doc: str | None = None,
        default: V | None | _NoDefaultType = _NoDefault,
    ) -> Callable[[RouteOrCallable[P]], Route[P]]:
        """
        Set a query parameter.

        Args:
            name: Name of the parameter.
            tps: Types that can be passed to the server. If empty, any is used.
            doc: Description of this query parameter.
            default: Default value to be used if not supplied.
        """

        def inner(func: RouteOrCallable[P]) -> Route[P]:
            route: Route[P] = query_impl(name, *tps, doc=doc, default=default)(func)
            self._push_route(route)
            return route

        return inner

    def body(
        self,
        name: str,
        *tps: type[V],
        doc: str | None = None,
        default: V | None | _NoDefaultType = _NoDefault,
    ) -> Callable[[RouteOrCallable[P]], Route[P]]:
        """
        Set a body parameter.

        Args:
            name: Name of the parameter.
            tps: Types that can be passed to the server. If empty, any is used.
            doc: Description of this body parameter.
            default: Default value to be used if not supplied.
        """

        def inner(func: RouteOrCallable[P]) -> Route[P]:
            route: Route[P] = body_impl(name, *tps, doc=doc, default=default)(func)
            self._push_route(route)
            return route

        return inner

    async def template(
        self,
        name: str | Path,
        directory: str | Path | None = _ConfigSpecified,
        engine: TemplateEngine | None = _ConfigSpecified,
        frame: Frame | None | _CurrentFrameType = _CurrentFrame,
        **parameters: Any,
    ) -> HTML:
        """
        Render a template with the specified engine.

        This is the direct variation of `template()` to prevent an import.
        """
        f: Frame | None
        if frame is _CurrentFrame:
            f = inspect.currentframe()
            assert f
            f = f.f_back
            assert f
        else:
            f = frame  # type: ignore

        return await template(name, directory, engine, f, app=self, **parameters)

    async def markdown(
        self,
        name: str | Path,
        *,
        directory: str | Path | None = _ConfigSpecified,
    ) -> HTML:
        """
        Convert a markdown file into HTML.

        This is the direct variation of `markdown()` to prevent an import.
        """
        return await markdown(name, directory=directory, app=self)

    @overload
    def context(
        self,
        r_or_none: RouteOrCallable[P],
    ) -> Route[P]: ...

    @overload
    def context(
        self,
        r_or_none: None = None,
    ) -> Callable[[RouteOrCallable[P]], Route[P]]: ...

    def context(
        self,
        r_or_none: RouteOrCallable[P] | None = None,
    ) -> Callable[[RouteOrCallable[P]], Route[P]] | Route[P]:
        return context_impl(r_or_none)

    async def _app(self, scope, receive, send) -> None:
        return await self.asgi_app_entry(scope, receive, send)

    def load(self, *routes: Route) -> None:
        """
        Load the app.
        This is automatically called most of the time, and should only be called manually during manual loading.

        Args:
            routes: Routes to load into the app.
        """
        if self.loaded:
            if routes:
                finalize(routes, self)
            Internal.warning("load called again")
            return

        if routes and (self.config.app.loader != "manual"):
            warnings.warn(_ROUTES_WARN_MSG)

        for index, i in enumerate(routes):
            if not isinstance(i, Route):
                raise TypeError(f"(index {index}) expected Route object, got {i}")

        with suppress(ImportError):
            import exceptiongroup
            from reactpy.backend.hooks import ConnectionContext
            from reactpy.core.layout import Layout
            from reactpy.core.serve import serve_layout

            @self.websocket("/_view/reactpy-stream")
            @self.query("route", str)
            async def reactpy_stream(ws: WebSocket, route: str):
                try:
                    page = self._reactive_sessions[route.strip("\n")]
                except KeyError:
                    return "Invalid route stream ID"

                await ws.accept()
                with suppress(exceptiongroup.ExceptionGroup):
                    await serve_layout(
                        Layout(ConnectionContext(page)),  # type: ignore
                        ws.send,  # type: ignore
                        partial(ws.receive, tp=dict),  # type: ignore
                    )

        if self.config.app.loader == "filesystem":
            load_fs(self, self.config.app.loader_path)
        elif self.config.app.loader == "simple":
            load_simple(self, self.config.app.loader_path)
        elif self.config.app.loader == "patterns":
            load_patterns(self, self.config.app.loader_path)
        elif self.config.app.loader == "custom":
            if not self._user_loader:
                raise InvalidCustomLoaderError("custom loader was not set")

            collected = self._user_loader(self, self.config.app.loader_path)
            if not isinstance(collected, CollectionsIterable):
                raise InvalidCustomLoaderError(
                    f"expected custom loader to return a list of routes, got {collected!r}"
                )
            finalize(collected, self)
        else:
            finalize([*(routes or ()), *self._manual_routes], self)

        self.loaded = True

        for r in self.loaded_routes:
            if not r.path:
                continue

            if r.path.startswith("/_view"):
                continue

            body: dict[str, InputDoc] = {}
            query: dict[str, InputDoc] = {}

            for i in r.inputs:
                if not isinstance(i, RouteInput):
                    continue

                target = body if i.is_body else query
                target[i.name] = InputDoc(
                    i.doc or "No description provided.", i.tp, i.default
                )

            if r.method:
                self._docs[(r.method.name, r.path)] = RouteDoc(
                    r.doc or "No description provided.", body, query
                )
            else:
                self._docs[
                    (
                        (
                            tuple([i.name for i in r.method_list])
                            if r.method_list
                            else (
                                "GET",
                                "POST",
                                "PUT",
                                "PATCH",
                                "DELETE",
                                "OPTIONS",
                            )
                        ),
                        r.path,
                    )
                ] = RouteDoc(r.doc or "No description provided.", body, query)

    async def _spawn(self, coro: Coroutine[Any, Any, Any]):
        loop = asyncio.get_event_loop()
        Internal.info(f"using event loop: {loop}")
        await self.build()
        Internal.info(f"spawning {coro}")

        task = loop.create_task(coro)

        if self.config.log.fancy:
            enter_server()

        self.running = True
        Internal.debug("here we go!")

        if (self.config.log.startup_message) and (not self.config.log.fancy):
            welcome()

        if self.config.dev:
            Service.warning(
                "Development mode is enabled, do not expect high performance."
            )

        async def subcoro():
            Service.info(
                f"Server running at http://{self.config.server.host}:{self.config.server.port} with backend [bold green]{self.config.server.backend}[/]"  # noqa
            )

        await asyncio.gather(task, subcoro())
        self.running = False

        if self.config.log.fancy:
            exit_server()

        Internal.info("server closed")

    def _run(self, start_target: Callable[..., Any] | None = None) -> Any:
        self.load()
        Internal.info("starting server!")
        server = self.config.server.backend
        uvloop_enabled = False

        if self.config.app.uvloop is True:
            try:
                import uvloop
            except ModuleNotFoundError as e:
                needs_dep("uvloop", e)
            uvloop.install()
            uvloop_enabled = True
        elif self.config.app.uvloop == "decide":
            with suppress(ModuleNotFoundError):
                import uvloop

                uvloop.install()
                uvloop_enabled = True

        def start(coro: Coroutine[Any, Any, Any]) -> None:
            try:
                (start_target or asyncio.run)(coro)
            except KeyboardInterrupt:
                Service.info("CTRL+C received, closing server.")
                exit()

        if server == "uvicorn":
            try:
                import uvicorn
            except ModuleNotFoundError as e:
                needs_dep("uvicorn", e, "servers")

            config = uvicorn.Config(
                self._app,
                port=self.config.server.port,
                host=str(self.config.server.host),
                log_level="debug" if self.config.dev else "info",
                lifespan="on",
                factory=False,
                interface="asgi3",
                loop="uvloop" if uvloop_enabled else "asyncio",
                **self.config.server.extra_args,
            )

            for log in (
                logging.getLogger("uvicorn"),
                logging.getLogger("uvicorn.error"),
                logging.getLogger("uvicorn.access"),
                logging.getLogger("uvicorn.asgi"),
            ):
                if self.config.log.server_logger and self.config.log.fancy:
                    log.addFilter(Hijack())
                log.disabled = not self.config.log.server_logger

            uvicorn_server = uvicorn.Server(config)
            return start(self._spawn(uvicorn_server.serve()))

        elif server == "hypercorn":
            try:
                import hypercorn
            except ModuleNotFoundError as e:
                needs_dep("hypercorn", e, "servers")

            for log in (
                logging.getLogger("hypercorn.error"),
                logging.getLogger("hypercorn.access"),
            ):
                if self.config.log.server_logger and self.config.log.fancy:
                    log.addFilter(Hijack())
                log.disabled = not self.config.log.server_logger

            from hypercorn.asyncio import serve

            conf = hypercorn.Config()
            conf.loglevel = "debug" if self.config.dev else "info"
            conf.bind = [
                f"{self.config.server.host}:{self.config.server.port}",
            ]

            for k, v in self.config.server.extra_args.items():
                setattr(conf, k, v)

            return start(self._spawn(serve(self._app, conf)))
        elif server == "daphne":
            try:
                import daphne as _
            except ModuleNotFoundError as e:
                needs_dep("daphne", e, "servers")

            from daphne.endpoints import build_endpoint_description_strings
            from daphne.server import Server

            endpoints = build_endpoint_description_strings(
                host=str(self.config.server.host),
                port=self.config.server.port,
            )

            for logger in (
                logging.getLogger("daphne.cli"),
                logging.getLogger("daphne.server"),
                logging.getLogger("daphne.http_protocol"),
            ):
                logger.disabled = not self.config.log.server_logger
                # default daphne log configuration
                level = (
                    _LEVELS[self.config.log.level]
                    if not isinstance(self.config.log.level, int)
                    else self.config.log.level
                )
                logger.setLevel(level)

                if self.config.log.server_logger:
                    logging.basicConfig(
                        level=level,
                        format="%(asctime)-15s %(levelname)-8s %(message)s",
                    )

                daphne_server = Server(
                    self._app, server_name="view.py", endpoints=endpoints
                )
                if self.config.log.server_logger and self.config.log.fancy:
                    logger.addFilter(Hijack())
            # mypy thinks asyncio.to_thread doesn't exist for some reason
            return start(
                self._spawn(asyncio.to_thread(daphne_server.run))  # type: ignore
            )
        else:
            raise NotImplementedError("viewserver is not implemented yet")

    def run(self, *, fancy: bool | None = None, force: bool = False) -> None:
        """
        Run the app.

        args:
            fancy: Override for the `fancy` parameter in configuration. It's useful to pass this parameter instead of modifying the configuration when debugging.
            force: Force the app to run, regardless of environment.
        """
        self._run_called = True
        if fancy is not None:
            self.config.log.fancy = fancy

        frame = inspect.currentframe()
        assert frame, "failed to get frame"
        assert frame.f_back, "frame has no f_back"

        back = frame.f_back
        base = os.path.basename(back.f_code.co_filename)
        app_path = self.config.app.app_path
        fname = app_path.split(":", maxsplit=1)[0]
        if base != fname:
            warnings.warn(
                f"ran app from {base}, but app path is {fname} in config",
            )

        if force:
            Internal.info("forcing app start")

        if force or (
            (not os.environ.get("_VIEW_RUN"))
            and (back.f_globals.get("__name__") == "__main__")
        ):
            self._run()
        else:
            Internal.info("called run, but env or scope prevented startup")

    async def build(self) -> None:
        """
        Run the default build steps for the app.
        """
        from .build import build_steps

        await build_steps(self)

    async def export(self, path: str | Path | None = None) -> None:
        """
        Export the app as static HTML.

        Args:
            path: Path to export files to. This is passed to `build_app`.
        """
        from .build import build_app

        await build_app(self, path=Path(path) if path else None)

    def run_threaded(self, *, daemon: bool = True) -> Thread:
        """
        Run the app in a thread.

        Args:
            daemon: Equivalent to the `daemon` parameter on `threading.Thread`
        """
        thread = Thread(target=self._run, daemon=daemon)
        thread.start()
        return thread

    def run_async(
        self,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        """
        Run the app in an event loop.

        Args:
            loop: `asyncio` event loop to use. If `None`, `asyncio.get_event_loop()` is called.
        """
        self._run((loop or asyncio.get_event_loop()).run_until_complete)

    def run_task(
        self,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> asyncio.Task[None]:
        """
        Run the app as an `asyncio` task.

        Args:
            loop: `asyncio` event loop to use. If `None`, `asyncio.get_event_loop()` is called.
        """
        return self._run((loop or asyncio.get_event_loop()).create_task)

    start = run

    def __repr__(self) -> str:
        return f"App(config={self.config!r})"

    @asynccontextmanager
    async def test(self):
        """
        Open the testing context.
        """
        self.load()
        await self.build()
        ctx = TestingContext(self.asgi_app_entry)
        try:
            yield ctx
        finally:
            await ctx.stop()

    @overload
    def docs(self, file: None = None) -> str: ...

    @overload
    def docs(self, file: TextIO) -> None: ...

    @overload
    def docs(
        self,
        file: Path,
        *,
        encoding: str = "utf-8",
        overwrite: bool = True,
    ) -> None: ...

    @overload
    def docs(
        self,
        file: str,
        *,
        encoding: str = "utf-8",
        overwrite: bool = True,
    ) -> None: ...

    def docs(
        self,
        file: str | TextIO | Path | None = None,
        *,
        encoding: str = "utf-8",
        overwrite: bool = True,
    ) -> str | None:
        """Generate documentation for the app."""
        self.load()
        md = markdown_docs(self._docs)

        if not file:
            return md

        if isinstance(file, str):
            if not overwrite:
                Path(file).write_text(md, encoding=encoding)
            else:
                with open(file, "w", encoding=encoding) as f:
                    f.write(md)
        elif isinstance(file, Path):
            if overwrite:
                with open(file, "w", encoding=encoding) as f:
                    f.write(md)
            else:
                file.write_text(md)
        else:
            file.write(md)

        return None


def new_app(
    *,
    start: bool = False,
    config_path: Path | str | None = None,
    config_directory: Path | str | None = None,
    app_dealloc: Callback | None = None,
    store: bool = True,
    config: Config | None = None,
) -> App:
    """
    Create a new view app.

    Args:
        start: Should the app be started automatically? (In a new thread)
        config_path: Path of the target configuration file
        config_directory: Directory path to search for a configuration
        app_dealloc: Callback to run when the App instance is freed from memory
        store: Whether to store the app, to allow use from get_app()
        config: Raw `Config` object to use instead of loading the config.

    Example:
        ```py
        from view import new_app

        app = new_app()

        # ...

        app.run()
        ```
    """
    config = config or load_config(
        path=Path(config_path) if config_path else None,
        directory=Path(config_directory) if config_directory else None,
    )

    app = App(config)

    if start:
        app.run_threaded()

    def finalizer():
        if "_VIEW_APP_ADDRESS" in os.environ:
            del os.environ["_VIEW_APP_ADDRESS"]

        if app_dealloc:
            app_dealloc()

    weakref.finalize(app, finalizer)

    if store:
        os.environ["_VIEW_APP_ADDRESS"] = str(id(app))
        # id() on CPython returns the address, but it is
        # implementation dependent.
        # However, view.py only supports CPython anyway

    return app


# This is forbidden pointers.py technology
# If anyone has a better way to do it, let me know

ctypes.pythonapi.Py_IncRef.argtypes = (ctypes.py_object,)


def get_app(*, address: int | None = None) -> App:
    """Get the last app created by `new_app`."""
    env = os.environ.get("_VIEW_APP_ADDRESS")
    addr = address or env

    if (not addr) and (not env):
        raise BadEnvironmentError("no view app registered")

    app: App = ctypes.cast(int(addr), ctypes.py_object).value  # type: ignore
    ctypes.pythonapi.Py_IncRef(app)
    return app
