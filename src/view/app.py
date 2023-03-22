from __future__ import annotations

import asyncio
import faulthandler
import importlib
import inspect
import logging
import os
from contextlib import contextmanager
from threading import Thread
from types import ModuleType as Module
from typing import Any, Coroutine

from _view import ViewApp

from ._loader import load_fs, load_simple
from ._logging import (Internal, Service, UvicornHijack, enter_server,
                       exit_server)
from .config import Config, JsonValue, load_config
from .typing import ViewRoute
from .util import debug as enable_debug


def _attempt_import(mod: str) -> Module:
    try:
        return importlib.import_module(mod)
    except ImportError as e:
        raise ImportError(
            f"{mod} is not installed! (`pip install {mod}`)"
        ) from e


class App(ViewApp):
    __slots__ = ("config", "running")

    def __init__(self, config: Config) -> None:
        self.config = config
        self._set_dev_state(config.app.dev)

        if config.app.dev:
            faulthandler.enable()

        if config.log.debug:
            enable_debug()

        assert isinstance(config.log.level, int)
        Service.log.setLevel(config.log.level)

        if (not config.app.dev) and (config.network):
            self.config.network.port = 80

        self.running = False
        self.user_config = None

    async def _app(self, scope, receive, send) -> None:
        await self.asgi_app_entry(scope, receive, send)

    def load(self):
        if self.config.app.load_strategy == "filesystem":
            load_fs(self, self.config.app.load_path)
        elif self.config.app.load_strategy == "simple":
            load_simple(self, self.config.app.load_path)

    async def _spawn(self, coro: Coroutine[Any, Any, Any]):
        Internal.info(f"spawning {coro}")

        task = asyncio.create_task(coro)
        if self.config.log.hijack:
            Internal.info("hijacking uvicorn")
            for log in (
                logging.getLogger("uvicorn.error"),
                logging.getLogger("uvicorn.access"),
            ):
                log.addFilter(UvicornHijack())

        if self.config.log.fancy:
            if not self.config.log.hijack:
                raise ValueError("hijack must be enabled for fancy mode")

            enter_server()

        self.running = True
        Internal.debug("here we go!")
        await task
        Internal.info("server closed")
        self.running = False

        if self.config.log.fancy:
            exit_server()

    def _run(self) -> None:
        Internal.info("starting server!")
        server = self.config.app.server

        if self.config.app.use_uvloop:
            uvloop = _attempt_import("uvloop")
            uvloop.install()

        Internal.info(f"using event loop: {asyncio.get_event_loop()}")

        if (self.config.network.port == 80) and (self.config.app.dev):
            Service.warning("using port 80 when development mode is enabled")

        if server == "uvicorn":
            uvicorn = _attempt_import("uvicorn")

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

            asyncio.run(self._spawn(server.serve()))

        elif server == "hypercorn":
            hypercorn = _attempt_import("hypercorn")
            conf = hypercorn.Config()
            conf.loglevel = "debug" if self.config.app.dev else "info"
            conf.bind = [
                f"{self.config.network.host}:{self.config.network.port}"
            ]

            for k, v in self.config.network.extra_args.items():
                setattr(conf, k, v)

            asyncio.run(
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

    @contextmanager
    def run_ctx(self):
        try:
            yield None
        finally:
            pass

    def run_threaded(self, *, daemon: bool = True) -> Thread:
        thread = Thread(target=self._run, daemon=daemon)
        thread.start()
        return thread

    start = run

    def __repr__(self) -> str:
        return f"App(config={self.config!r})"


def new_app(
    *,
    config_path: str | None = None,
    overrides: dict[str, JsonValue] | None = None,
    default: bool = False,
    start: bool = False,
    **config_overrides: JsonValue,
) -> App:
    config = load_config(
        config_path,
        {**(overrides or {}), **config_overrides},
        default=default,
    )
    app = App(config)

    if start:
        app.run_threaded()

    return app
