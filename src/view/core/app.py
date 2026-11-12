"""
Primary app implementation.
"""

from __future__ import annotations

import contextlib
import contextvars
from dataclasses import dataclass, field
import json
import os
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Generator, MutableSequence
from importlib.metadata import Distribution, PackageNotFoundError
from multiprocessing import Process
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Generic,
    ParamSpec,
    TypeAlias,
    TypeVar,
    Unpack,
    override,
)
import asyncio
from threading import Event, Thread

from view.core.request import Method, Request
from view.core.response import (
    Response,
    ResponseLike,
    ViewResult,
    wrap_view_result,
)
from view.core.router import FoundRoute, Route, Router, RouteView
from view.core.status_codes import (
    Forbidden,
    HTTPError,
    InternalServerError,
    NotFound,
)
from view.exceptions import InvalidTypeError
from view.logs import LogLevels, LogManager
from view.responses import FileResponse
from view.run.servers import ServerConfigArgs, run_app_on_any_server
from view.utils import StartStopMixin, reraise
from queue import Queue

if TYPE_CHECKING:
    from view.run.asgi import ASGIProtocol
    from view.run.wsgi import WSGIProtocol

__all__ = "App", "BaseApp", "as_app"

T = TypeVar("T")
P = ParamSpec("P")


def _is_development_mode() -> bool:
    devmode_variable = os.environ.get("VIEW_DEVMODE")
    if devmode_variable is not None:
        if not devmode_variable.isdigit():
            raise RuntimeError(
                f"Invalid value for VIEW_DEVMODE: {devmode_variable!r}"
            )

        return bool(int(devmode_variable))

    try:
        view_distribution = Distribution.from_name("view.py")
    except PackageNotFoundError:
        # view.py isn't even installed -- we're definitely in some sort of
        # local copy.
        return True
    json_data = view_distribution.read_text("direct_url.json")
    if json_data is None:
        return False

    return json.loads(json_data).get("dir_info", {}).get("editable", False)


_LifecycleT = TypeVar("_LifecycleT")
LifecycleFunction: TypeAlias = Callable[
    [],
    contextlib.AbstractAsyncContextManager[T]
    | contextlib.AbstractContextManager[T],
]
_MISSING = object()


@dataclass(slots=True)
class LifecycleItem(Generic[_LifecycleT]):
    function: LifecycleFunction
    _result: _LifecycleT | Any = field(default=_MISSING, init=False)

    def __call__(self) -> _LifecycleT:
        if self._result is _MISSING:
            raise RuntimeError(
                f"lifecycle item {self.function.__name__} has not been invoked yet"
            )

        return self._result

    @contextlib.asynccontextmanager
    async def execute(self) -> AsyncGenerator[None]:
        async with contextlib.AsyncExitStack() as stack:
            context = self.function()
            if isinstance(context, contextlib.AbstractAsyncContextManager):
                result = await stack.enter_async_context(context)
            else:
                assert isinstance(context, contextlib.AbstractContextManager)
                result = stack.enter_context(context)

            self._result = result
            yield


class BaseApp(StartStopMixin, ABC):
    """Base view.py application."""

    _CURRENT_APP = contextvars.ContextVar["BaseApp"]("Current app being used.")

    def __init__(self) -> None:
        super().__init__()
        self._request = contextvars.ContextVar[Request]("request")
        self._production: bool | None = None

        # We use a private variable for this to artificially disallow people
        # from writing to development_mode.
        self._development_mode: bool = _is_development_mode()

        self.log_manager = LogManager(
            level=LogLevels.DEBUG if self.development_mode else LogLevels.INFO
        )
        """
        The log manager used by the app.
        """

        self.logger = self.log_manager.create_logger("app")

        self.lifecycle_items: MutableSequence[LifecycleItem] = []

    @property
    def development_mode(self) -> bool:
        """
        Whether view.py is in "development mode". If this is ``True``, then
        that means you're working on contributing to the library itself.

        This cannot be set from Python. If you'd like to control this behavior,
        set the ``VIEW_DEVMODE`` environment variable to ``1`` or ``0``.
        """
        return self._development_mode

    def shut_up(self) -> None:
        """
        Stop all log output.
        """

        self.log_manager.disabled = True

    @property
    def debug(self) -> bool:
        """
        Is the app in debug mode?

        If debug mode is enabled, some extra checks and settings are enabled
        to improve the development experience, at the cost of being slower and
        less secure.
        """
        if self._production is None:
            return __debug__

        return self._production

    @contextlib.contextmanager
    def request_context(self, request: Request) -> Generator[None]:
        """
        Enter a context for the given request.
        """
        app_token = self._CURRENT_APP.set(self)
        request_token = self._request.set(request)
        try:
            yield
        finally:
            self._request.reset(request_token)
            self._CURRENT_APP.reset(app_token)

    @classmethod
    def current_app(cls) -> BaseApp:
        return cls._CURRENT_APP.get()

    def current_request(self) -> Request:
        """
        Get the current request being handled.
        """
        return self._request.get()

    @abstractmethod
    async def process_request(self, request: Request) -> Response:
        """
        Get the response from the server for a given request.
        """

    def _build_wsgi_callable(
        self, queue: Queue[WSGIProtocol], shutdown_event: Event
    ) -> None:
        """
        Build an event loop in the current thread and emit a WSGI callable
        bound to it.
        """
        from view.run.wsgi import wsgi_for_app

        loop = asyncio.new_event_loop()

        async def _run_server():
            async with self:
                wsgi_app = wsgi_for_app(self, loop)
                queue.put_nowait(wsgi_app)
                await asyncio.to_thread(shutdown_event.wait)

        try:
            loop.run_until_complete(_run_server())
        finally:
            loop.close()

    @contextlib.contextmanager
    def wsgi(self) -> Generator[WSGIProtocol]:
        """
        Build a WSGI callable for the app.
        """
        queue = Queue["WSGIProtocol"](maxsize=1)
        shutdown_event = Event()
        thread = Thread(
            target=self._build_wsgi_callable, args=(queue, shutdown_event)
        )
        thread.start()
        try:
            yield queue.get()
        finally:
            shutdown_event.set()
            thread.join()

    def asgi(self) -> ASGIProtocol:
        """
        Get the ASGI callable for this app.
        """
        from view.run.asgi import asgi_for_app

        return asgi_for_app(self)

    def lifecycle(
        self, function: LifecycleFunction[_LifecycleT]
    ) -> LifecycleItem[_LifecycleT]:
        item = LifecycleItem(function)
        self.lifecycle_items.append(item)
        return item

    @override
    async def start(self) -> None:
        async with self.log_manager, contextlib.AsyncExitStack() as stack:
            for item in self.lifecycle_items:
                await stack.enter_async_context(item.execute())

            self.log_manager.print_startup_message()

            if self.development_mode:
                self.logger.info("You're in development mode!")
                self.logger.info(
                    "Development mode implies that you're working on view.py itself and plan on contributing to the library."
                )
                self.logger.info(
                    "If that doesn't sound correct, set VIEW_DEVMODE to 0."
                )

            self.logger.info("Serving app on http://localhost:5000")

            self._wakeup_event.set()
            while self.running:
                await asyncio.sleep(1)

            self.logger.info("Server is shutting down!")

    def run(self, **kwargs: Unpack[ServerConfigArgs]) -> None:
        """
        Run the app, starting the event loop and server.
        """

        run_app_on_any_server(self, **kwargs)

    def run_detached(
        self,
        **kwargs: Unpack[ServerConfigArgs],
    ) -> Process:
        """
        Run the app in a separate process. This means that the server is
        killable.
        """

        process = Process(
            target=self.run,
            kwargs=kwargs,
        )
        process.start()
        return process

    async def _execute_view_internal(
        self,
        view: Callable[P, ViewResult],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Response:
        self.logger.debug(f"Executing view: {view}")
        try:
            result = view(*args, **kwargs)
            return await wrap_view_result(result)
        except HTTPError as error:
            self.logger.warning(f"HTTP Error {error.status_code}")
            raise

    async def execute_view(
        self, view: Callable[P, ViewResult], *args: P.args, **kwargs: P.kwargs
    ) -> Response:
        try:
            return await self._execute_view_internal(view, *args, **kwargs)
        except BaseException as exception:
            # Let HTTP errors pass through, so the caller can deal with it
            if isinstance(exception, HTTPError):
                raise
            self.logger.exception("Error while processing response")

            if __debug__:
                raise InternalServerError.from_current_exception() from exception

            raise InternalServerError from exception


SingleView = Callable[["Request"], ViewResult]


class SingleViewApp(BaseApp):
    """
    Application with a single view function that
    processes all requests.
    """

    def __init__(self, view: SingleView) -> None:
        super().__init__()
        self.view = view

    async def process_request(self, request: Request) -> Response:
        with self.request_context(request):
            try:
                return await self.execute_view(self.view, request)
            except HTTPError as error:
                return error.as_response()


def as_app(view: SingleView, /) -> SingleViewApp:
    """
    Decorator for using a single function as an app.
    """
    if __debug__ and not callable(view):
        raise InvalidTypeError(view, Callable)

    return SingleViewApp(view)


RouteDecorator: TypeAlias = Callable[[RouteView], Route]
SubRouterView: TypeAlias = Callable[
    [str], ResponseLike | Awaitable[ResponseLike]
]
SubRouterViewT = TypeVar("SubRouterViewT", bound=SubRouterView)


class App(BaseApp):
    """
    An application containing an automatic routing mechanism
    and error handling.
    """

    def __init__(self, *, router: Router | None = None) -> None:
        super().__init__()
        self.router = router or Router()

    async def _process_request_internal(self, request: Request) -> Response:
        self.logger.info(f"{request.method} on route {request.path}")
        found_route: FoundRoute | None = self.router.lookup_route(
            request.path, request.method
        )
        if found_route is None:
            raise NotFound

        # Extend instead of replacing?
        request.path_parameters = found_route.path_parameters
        return await self.execute_view(found_route.route.view)

    async def process_request(self, request: Request) -> Response:
        with self.request_context(request):
            try:
                return await self._process_request_internal(request)
            except HTTPError as error:
                error_view = self.router.lookup_error(type(error))
                if error_view is not None:
                    return await self.execute_view(error_view)

                return error.as_response()

    def route(self, path: str, /, *, method: Method) -> RouteDecorator:
        """
        Decorator interface for adding a route to the app.
        """

        if __debug__ and not isinstance(path, str):
            raise InvalidTypeError(path, str)

        if __debug__ and not isinstance(method, Method):
            raise InvalidTypeError(method, Method)

        def decorator(view: RouteView, /) -> Route:
            return self.router.push_route(view, path, method)

        return decorator

    def get(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a GET route.
        """
        return self.route(path, method=Method.GET)

    def post(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a POST route.
        """
        return self.route(path, method=Method.POST)

    def put(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a PUT route.
        """
        return self.route(path, method=Method.PUT)

    def patch(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a PATCH route.
        """
        return self.route(path, method=Method.PATCH)

    def delete(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a DELETE route.
        """
        return self.route(path, method=Method.DELETE)

    def connect(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a CONNECT route.
        """
        return self.route(path, method=Method.CONNECT)

    def options(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding an OPTIONS route.
        """
        return self.route(path, method=Method.OPTIONS)

    def trace(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a TRACE route.
        """
        return self.route(path, method=Method.TRACE)

    def head(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a HEAD route.
        """
        return self.route(path, method=Method.HEAD)

    def error(
        self, status: int | type[HTTPError], /
    ) -> Callable[[RouteView], RouteView]:
        """
        Decorator interface for adding an error handler to the app.
        """

        def decorator(view: RouteView, /) -> RouteView:
            self.router.push_error(status, view)
            return view

        return decorator

    def subrouter(
        self, path: str
    ) -> Callable[[SubRouterViewT], SubRouterViewT]:
        if __debug__ and not isinstance(path, str):
            raise InvalidTypeError(path, str)

        def decorator(function: SubRouterViewT, /) -> SubRouterViewT:
            if __debug__ and not callable(function):
                raise InvalidTypeError(Callable, function)

            def router_function(path_from_url: str) -> Route:
                def route() -> ResponseLike | Awaitable[ResponseLike]:
                    return function(path_from_url)

                return Route(route, path_from_url, Method.GET)

            self.router.push_subrouter(router_function, path)
            return function

        return decorator

    def static_files(self, path: str, directory: str | Path) -> None:
        if __debug__ and not isinstance(directory, (str, Path)):
            raise InvalidTypeError(directory, str, Path)

        directory = Path(directory)

        @self.subrouter(path)
        def serve_static_file(path_from_url: str) -> ResponseLike:
            file = directory / path_from_url
            if not file.is_file():
                raise NotFound

            if not file.is_relative_to(directory):
                raise Forbidden

            with reraise(Forbidden, OSError):
                return FileResponse.from_file(file)
