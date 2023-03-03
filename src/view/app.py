from __future__ import annotations

import asyncio
import importlib
import os
from contextlib import contextmanager
from threading import Thread
from types import ModuleType as Module
from typing import TYPE_CHECKING, NoReturn

from _view import ViewApp

from .config import Config, load_config

if TYPE_CHECKING:
    from _view import ViewRoute


def _attempt_import(mod: str) -> Module:
    try:
        return importlib.import_module(mod)
    except ImportError as e:
        raise ImportError(
            f"{mod} is not installed! (`pip install {mod}`)"
        ) from e


class App(ViewApp):
    __slots__ = ("config",)

    def __init__(self, config: Config) -> None:
        self.config = config
        self._set_dev_state(config.app.dev)

    async def _app(self, scope, receive, send) -> None:
        await self.asgi_app_entry(scope, receive, send)

    def get(self, route: str, context: bool = True):
        def decorator(func: ViewRoute):
            self._get(route, func, 0)

        return decorator

    def _run(self) -> None:
        server = self.config.app.server

        if self.config.app.use_uvloop:
            uvloop = _attempt_import("uvloop")
            uvloop.install()

        if server == "uvicorn":
            uvicorn = _attempt_import("uvicorn")
            uvicorn.run(
                self.asgi_app_entry,
                port=self.config.network.port,
                host=self.config.network.host,
                log_level="debug" if self.config.app.dev else "info",
                lifespan="on",
                factory=False,
                interface="asgi3",
            )
        elif server == "hypercorn":
            hypercorn = _attempt_import("hypercorn")
            conf = hypercorn.Config()
            conf.loglevel = "debug" if self.config.app.dev else "info"
            asyncio.run(
                importlib.import_module("hypercorn.asyncio").serve(
                    self.asgi_app_entry, conf
                )
            )
        else:
            raise NotImplementedError("viewserver is not implemented yet")

    def run(self) -> NoReturn:
        if not os.environ.get("_VIEW_RUN"):
            self._run()
        exit(0)

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


def new_app() -> App:
    return App(load_config())
