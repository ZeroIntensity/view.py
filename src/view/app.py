from __future__ import annotations

import asyncio
import faulthandler
import importlib
import inspect
import json
import logging
import os
import sys
import warnings
import weakref
from dataclasses import dataclass as apply_dataclass
from functools import lru_cache
from multiprocessing import Process
from pathlib import Path
from threading import Thread
from types import TracebackType as Traceback
from typing import (Any, Awaitable, Callable, Coroutine, Generic, TypeVar,
                    get_type_hints, overload)

from rich import print
from rich.traceback import install

from _view import ViewApp

from ._loader import finalize, load_fs, load_simple
from ._logging import (Internal, Service, UvicornHijack, enter_server,
                       exit_server, format_warnings)
from ._util import attempt_import, make_hint
from .config import Config, JsonValue, load_config, load_path_simple
from .exceptions import ViewError
from .routing import (Route, RouteOrCallable, delete, get, options, patch,
                      post, put)
from .util import debug as enable_debug

get_type_hints = lru_cache(get_type_hints)

__all__ = "App", "new_app"

S = TypeVar("S", int, str, dict, bool)
A = TypeVar("A")

_ROUTES_WARN_MSG = (
    "routes argument should only be passed when load strategy is manual"
)

B = TypeVar("B", bound=BaseException)


class App(ViewApp, Generic[A]):
    def __init__(self, config: Config) -> None:
        self.config = config
        self._set_dev_state(config.app.dev)
        self._manual_routes: list[Route] = []
        self.routes: list[Route] = []
        self.loaded: bool = False
        self.running = False

        assert isinstance(config.log.level, int)
        Service.log.setLevel(config.log.level)

        if config.app.dev:
            if os.environ.get("VIEW_PROD") is not None:
                Service.warning("VIEW_PROD is set but dev is set to true")

            format_warnings()
            weakref.finalize(self, self._finalize)
            install(show_locals=True)
            rich_handler = sys.excepthook

            def _hook(tp: type[B], value: B, traceback: Traceback) -> None:
                rich_handler(tp, value, traceback)
                os.environ["_VIEW_CANCEL_FINALIZERS"] = "1"

                if isinstance(value, ViewError):
                    if value.hint:
                        print(value.hint)

            sys.excepthook = _hook
            faulthandler.enable()
        else:
            os.environ["VIEW_PROD"] = "1"

        if config.log.debug:
            enable_debug()

        if (not config.app.dev) and (config.network):
            self.config.network.port = 80

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
        split = self.config.app.path.split(":", maxsplit=1)

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

    def _load_settings(self, ob: Any) -> None:
        for k, tp in get_type_hints(ob).items():
            if tp not in {str, int, dict, bool}:
                raise TypeError(f"bad type for {k!r}: {tp}")

        self.user_settings = ob

    @overload
    def settings(self, ob: type[A], *, dataclass: bool = ...) -> type[A]:
        ...

    @overload
    def settings(
        self,
        ob: None = ...,
        *,
        dataclass: bool = True,
    ) -> Callable[[type[A]], type[Any]]:
        ...

    def settings(
        self,
        ob: type[A] | None = None,
        *,
        dataclass: bool = False,
    ) -> type[A] | Callable[[type[A]], type[Any]]:
        if not ob:

            def inner(cls: type[A]) -> type[Any]:
                if dataclass:
                    cls = apply_dataclass(cls)
                self._load_settings(cls)
                return cls

            return inner

        self._load_settings(ob)
        return ob

    def supply(self, ob: type[A] | dict[str, Any]) -> None:
        if isinstance(ob, dict):
            self._supply(ob)
        elif self.user_settings and isinstance(ob, self.user_settings):
            self._supply(
                {k: getattr(ob, k) for k in dir(ob) if not k.startswith("__")}
            )
        else:
            raise ValueError(f"{ob!r} is not a suppliable type")

    async def _app(self, scope, receive, send) -> None:
        return await self.asgi_app_entry(scope, receive, send)

    def get_setting(self, key: str) -> S:
        assert (
            self._supplied_config is not None
        ), "config has not been loaded or set"
        return self._supplied_config[key]

    def load(self, routes: list[Route] | None = None) -> None:
        if self.loaded:
            Internal.warning("load called twice")
            return

        if self.config.app.load_strategy == "filesystem":
            if routes:
                warnings.warn(_ROUTES_WARN_MSG)
            load_fs(self, self.config.app.load_path)
        elif self.config.app.load_strategy == "simple":
            if routes:
                warnings.warn(_ROUTES_WARN_MSG)
            load_simple(self, self.config.app.load_path)
        else:
            finalize([*(routes or ()), *self._manual_routes], self)

        self.loaded = True
        if not self.user_settings:
            return

        paths = (
            "app_config",
            "app",
            "config",
        )
        path: Path | None = None

        for ext in ("toml", "json"):
            for name in paths:
                tmp = Path(name).with_suffix(ext)

                if tmp.exists():
                    path = tmp
                    break

        if not path:
            if self._supplied_config is None:
                raise FileNotFoundError("no user config exists")
            return

        loaded = load_path_simple(path)
        self._supply(loaded)

    def _supply(self, loaded: dict[str, Any]) -> None:
        if self._supplied_config is None:
            self._supplied_config = {}

        for k, tp in get_type_hints(self.user_settings).items():
            value = loaded.get(k)

            if not value:
                raise RuntimeError(f"missing key in user settings: {k!r}")

            if tp is str:
                self._supplied_config[k] = str(value)

            elif tp is bool:
                if isinstance(tp, bool):
                    self._supplied_config[k] = value
                    return

                value = str(value).lower()
                if value not in {"true", "false"}:
                    raise ValueError(f"{value!r} is not true or false")

                self._supplied_config[k] = value == "true"

            elif tp is int:
                if isinstance(tp, int):
                    self._supplied_config[k] = value
                    return

                try:
                    self._supplied_config[k] = int(value)
                except ValueError:
                    raise ValueError(f"{value!r} is not int-like") from None

            elif tp is dict:
                try:
                    json.loads(value)
                except ValueError:
                    raise ValueError(f"{value!r} is invalid JSON")

    async def _spawn(self, coro: Coroutine[Any, Any, Any]):
        Internal.info(f"using event loop: {asyncio.get_event_loop()}")
        Internal.info(f"spawning {coro}")

        task = asyncio.create_task(coro)
        if self.config.log.hijack:
            if self.config.app.server == "uvicorn":
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

    def _run(
        self, start_target: Callable[[Awaitable[Any]], None] | None = None
    ) -> None:
        self.load()
        Internal.info("starting server!")
        server = self.config.app.server

        if self.config.app.use_uvloop:
            uvloop = attempt_import("uvloop")
            uvloop.install()

        if (self.config.network.port == 80) and (self.config.app.dev):
            Service.warning("using port 80 when development mode is enabled")

        start = start_target or asyncio.run

        if server == "uvicorn":
            uvicorn = attempt_import("uvicorn")

            config = uvicorn.Config(
                self.asgi_app_entry,
                port=self.config.network.port,
                host=self.config.network.host,
                log_level="debug" if self.config.app.dev else "info",
                lifespan="on",
                factory=False,
                interface="asgi3",
                loop="uvloop" if self.config.app.use_uvloop else "asyncio",
                **self.config.network.extra_args,
            )
            server = uvicorn.Server(config)

            start(self._spawn(server.serve()))

        elif server == "hypercorn":
            hypercorn = attempt_import("hypercorn")
            conf = hypercorn.Config()
            conf.loglevel = "debug" if self.config.app.dev else "info"
            conf.bind = [
                f"{self.config.network.host}:{self.config.network.port}"
            ]

            for k, v in self.config.network.extra_args.items():
                setattr(conf, k, v)

            start(
                importlib.import_module("hypercorn.asyncio").serve(
                    self._app, conf
                )
            )
        else:
            raise NotImplementedError("viewserver is not implemented yet")

    def run(self) -> None:
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

    def run_proc(self) -> Process:
        proc = Process(target=self._run)
        proc.start()
        return proc

    async def run_async(self, loop: asyncio.AbstractEventLoop):
        self._run((loop or asyncio.get_event_loop()).run_until_complete)

    start = run

    def __repr__(self) -> str:
        return f"App(config={self.config!r})"


def new_app(
    *,
    config_path: str | None = None,
    overrides: dict[str, JsonValue] | None = None,
    start: bool = False,
    **config_overrides: JsonValue,
) -> App:
    config = load_config(
        config_path,
        {**(overrides or {}), **config_overrides},
    )
    app = App(config)

    if start:
        app.run_threaded()

    return app
