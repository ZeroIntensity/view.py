from __future__ import annotations

import asyncio
import faulthandler
import importlib
import inspect
import logging
import os
import sys
import warnings
import weakref
from contextlib import suppress
from functools import lru_cache
from threading import Thread
from types import TracebackType as Traceback
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    TypeVar,
    get_type_hints,
)
from pathlib import Path
from rich import print
from rich.traceback import install
from .typing import Callback
from _view import ViewApp
from io import UnsupportedOperation
from ._loader import finalize, load_fs, load_simple
from ._logging import (
    Internal,
    Service,
    UvicornHijack,
    enter_server,
    exit_server,
    format_warnings,
)
from ._parsers import supply_parsers
from ._util import attempt_import, make_hint
from .config import Config, load_config
from .exceptions import MissingLibraryError, ViewError
from .routing import (
    Route,
    RouteOrCallable,
    delete,
    get,
    options,
    patch,
    post,
    put,
)
from .util import debug as enable_debug

get_type_hints = lru_cache(get_type_hints)

__all__ = "App", "new_app"

S = TypeVar("S", int, str, dict, bool)
A = TypeVar("A")

_ROUTES_WARN_MSG = "routes argument should only be passed when load strat"

B = TypeVar("B", bound=BaseException)


class App(ViewApp, Generic[A]):
    def __init__(self, config: Config) -> None:
        supply_parsers(self)
        self.config = config
        self._set_dev_state(config.dev)
        self._manual_routes: list[Route] = []
        self.routes: list[Route] = []
        self.loaded: bool = False
        self.running = False
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

            if config.log.pretty_tracebacks:
                install(show_locals=True)

            rich_handler = sys.excepthook

            def _hook(tp: type[B], value: B, traceback: Traceback) -> None:
                rich_handler(tp, value, traceback)
                os.environ["_VIEW_CANCEL_FINALIZERS"] = "1"

                if isinstance(value, ViewError):
                    if value.hint:
                        print(value.hint)

            sys.excepthook = _hook
            with suppress(UnsupportedOperation):
                faulthandler.enable()
        else:
            os.environ["VIEW_PROD"] = "1"

        if config.log.level == "debug":
            enable_debug()

        self.running = False
        self.user_settings: type[A] | None = None
        self._supplied_config: dict[str, Any] | None = {}

    def _finalize(self) -> None:
        if os.environ.get("_VIEW_CANCEL_FINALIZERS"):
            return

        if self.loaded:
            return

        warnings.warn(
            "load() was never called (did you forget to start the app?)"
        )
        split = self.config.app.app_path.split(":", maxsplit=1)

        if len(split) != 2:
            return

        app_name = split[1]

        print(
            make_hint(
                "Add this to your code",
                split[0],
                line=-1,
                prepend=f"\n{app_name}.run()",
            )
        )

    def _method_wrapper(
        self,
        path: str,
        doc: str | None,
        target: Callable[..., Any],
        # i dont really feel like typing this properly
    ) -> Callable[[RouteOrCallable], Route]:
        def inner(route: RouteOrCallable) -> Route:
            new_route = target(path, doc)(route)
            self._manual_routes.append(new_route)
            return new_route

        return inner

    def get(self, path: str, *, doc: str | None = None):
        return self._method_wrapper(path, doc, get)

    def post(self, path: str, *, doc: str | None = None):
        return self._method_wrapper(path, doc, post)

    def delete(self, path: str, *, doc: str | None = None):
        return self._method_wrapper(path, doc, delete)

    def patch(self, path: str, *, doc: str | None = None):
        return self._method_wrapper(path, doc, patch)

    def put(self, path: str, *, doc: str | None = None):
        return self._method_wrapper(path, doc, put)

    def options(self, path: str, *, doc: str | None = None):
        return self._method_wrapper(path, doc, options)

    async def _app(self, scope, receive, send) -> None:
        return await self.asgi_app_entry(scope, receive, send)

    def load(self, routes: list[Route] | None = None) -> None:
        if self.loaded:
            Internal.warning("load called twice")
            return

        if self.config.app.loader == "filesystem":
            if routes:
                warnings.warn(_ROUTES_WARN_MSG)
            load_fs(self, self.config.app.loader_path)
        elif self.config.app.loader == "simple":
            if routes:
                warnings.warn(_ROUTES_WARN_MSG)
            load_simple(self, self.config.app.loader_path)
        else:
            finalize([*(routes or ()), *self._manual_routes], self)

        self.loaded = True

    async def _spawn(self, coro: Coroutine[Any, Any, Any]):
        Internal.info(f"using event loop: {asyncio.get_event_loop()}")
        Internal.info(f"spawning {coro}")

        task = asyncio.create_task(coro)
        if self.config.log.hijack:
            if self.config.server.backend == "uvicorn":
                Internal.info("hijacking uvicorn")
                for log in (
                    logging.getLogger("uvicorn.error"),
                    logging.getLogger("uvicorn.access"),
                ):
                    log.addFilter(UvicornHijack())
            else:
                Internal.info("hijacking hypercorn")

        if self.config.log.fancy:
            if not self.config.log.hijack:
                raise ValueError("hijack must be enabled for fancy mode")

            enter_server()

        self.running = True
        Internal.debug("here we go!")
        await task
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
            uvloop = attempt_import("uvloop")
            uvloop.install()
            uvloop_enabled = True
        elif self.config.app.uvloop == "decide":
            with suppress(MissingLibraryError):
                uvloop = attempt_import("uvloop")
                uvloop.install()
                uvloop_enabled = True

        start = start_target or asyncio.run

        if server == "uvicorn":
            uvicorn = attempt_import("uvicorn")

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
            server = uvicorn.Server(config)

            return start(self._spawn(server.serve()))

        elif server == "hypercorn":
            hypercorn = attempt_import("hypercorn")
            conf = hypercorn.Config()
            conf.loglevel = "debug" if self.config.dev else "info"
            conf.bind = [
                f"{self.config.server.host}:{self.config.server.port}",
            ]

            for k, v in self.config.server.extra_args.items():
                setattr(conf, k, v)

            return start(
                importlib.import_module("hypercorn.asyncio").serve(
                    self._app, conf
                )
            )
        else:
            raise NotImplementedError("viewserver is not implemented yet")

    def run(self, *, fancy: bool | None = None) -> None:
        if fancy is not None:
            self.config.log.fancy = fancy

        frame = inspect.currentframe()
        assert frame, "failed to get frame"
        assert frame.f_back, "frame has no f_back"

        back = frame.f_back

        if (not os.environ.get("_VIEW_RUN")) and (
            back.f_globals.get("__name__") == "__main__"
        ):
            self._run()
        else:
            Internal.info("called run, but env or scope prevented startup")

    def run_threaded(self, *, daemon: bool = True) -> Thread:
        thread = Thread(target=self._run, daemon=daemon)
        thread.start()
        return thread

    def run_async(
        self,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self._run((loop or asyncio.get_event_loop()).run_until_complete)

    def run_task(
        self,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> asyncio.Task[None]:
        return self._run((loop or asyncio.get_event_loop()).create_task)

    start = run

    def __repr__(self) -> str:
        return f"App(config={self.config!r})"


def new_app(
    *,
    start: bool = False,
    config_path: Path | str | None = None,
    config_directory: Path | str | None = None,
    post_init: Callback | None = None,
    app_dealloc: Callback | None = None,
) -> App:
    """Create a new view app.

    Args:
        start: Should the app be started automatically? (In a new thread)
        config_path: Path of the target configuration file
        config_directory: Directory path to search for a configuration
        post_init: Callback to run after the App instance has been created
        app_dealloc: Callback to run when the App instance is freed from memory
    """
    config = load_config(
        path=Path(config_path) if config_path else None,
        directory=Path(config_directory) if config_directory else None,
    )

    app = App(config)

    if post_init:
        post_init()

    if start:
        app.run_threaded()

    if app_dealloc:
        weakref.finalize(app, app_dealloc)

    return app
