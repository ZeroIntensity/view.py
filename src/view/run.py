from __future__ import annotations

import warnings
from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, TypeAlias

if TYPE_CHECKING:
    from view.app import BaseApp
    from view.wsgi import WSGIProtocol

__all__ = ("ServerSettings",)

StartServer: TypeAlias = Callable[[], None]


@dataclass(slots=True, frozen=True)
class ServerSettings:
    """
    Dataclass representing server settings that can be used to start
    serving an app.
    """

    app: "BaseApp"
    port: int
    host: str
    hint: str | None = None

    def run_uvicorn(self) -> None:
        import uvicorn

        uvicorn.run(self.app.asgi(), host=self.host, port=self.port)

    def run_hypercorn(self) -> None:
        import asyncio

        import hypercorn
        from hypercorn.asyncio import serve

        config = hypercorn.Config()
        config.bind = [f"{self.host}:{self.port}"]
        asyncio.run(serve(self.app.asgi(), config))  # type: ignore

    def run_daphne(self) -> None:
        from daphne.endpoints import build_endpoint_description_strings
        from daphne.server import Server

        endpoints = build_endpoint_description_strings(
            host=self.host,
            port=self.port,
        )
        server = Server(self.app.asgi(), endpoints=endpoints)
        server.run()

    def run_gunicorn(self) -> None:
        from gunicorn.app.base import BaseApplication

        class GunicornRunner(BaseApplication):
            def __init__(
                self, app: WSGIProtocol, options: dict[str, Any] | None = None
            ) -> None:
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                assert self.cfg is not None
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key, value)

            def load(self):
                return self.application

        runner = GunicornRunner(self.app.wsgi(), {"bind": f"{self.host}:{self.port}"})
        runner.run()

    def run_werkzeug(self) -> None:
        from werkzeug.serving import run_simple

        run_simple(self.host, self.port, self.app.wsgi())

    def run_wsgiref(self) -> None:
        from wsgiref.simple_server import make_server

        with make_server(self.host, self.port, self.app.wsgi()) as server:
            server.serve_forever()

    def run_app_on_any_server(self) -> None:
        """
        Run the app on the nearest available ASGI or WSGI server.

        This will always succeed, as it will fall back to the standard
        `wsgiref` module if no other server is installed.
        """
        servers: dict[str, StartServer] = {
            "uvicorn": self.run_uvicorn,
            "hypercorn": self.run_hypercorn,
            "daphne": self.run_daphne,
            "gunicorn": self.run_gunicorn,
            "werkzeug": self.run_werkzeug,
            "wsgiref": self.run_wsgiref,
        }
        if self.hint is not None:
            try:
                start_server = servers[self.hint]
            except KeyError as key_error:
                raise ValueError(f"{self.hint!r} is not a known server") from key_error

            try:
                return start_server()
            except ImportError:
                warnings.warn(f"{self.hint} is not installed")

        for start_server in servers.values():
            with suppress(ImportError):
                return start_server()
