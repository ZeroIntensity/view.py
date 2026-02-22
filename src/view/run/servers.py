"""
Magically run applications on some common servers.
"""

from __future__ import annotations

from collections.abc import Callable, MutableMapping
from contextlib import suppress
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    NotRequired,
    TypeAlias,
    TypedDict,
    Unpack,
)

if TYPE_CHECKING:
    from view.core.app import BaseApp
    from view.run.wsgi import WSGIProtocol

from view.exceptions import ViewError

__all__ = ("run_app_on_any_server",)


class BadServerError(ViewError):
    """
    Something is wrong with the selected server.

    This generally means that the target server isn't installed or doesn't
    exist (either not supported by view.py or there's a typo present).
    """


class ServerConfigArgs(TypedDict):
    host: NotRequired[str]
    port: NotRequired[int]
    production: NotRequired[bool]
    server_hint: NotRequired[str]


@dataclass(slots=True, frozen=True)
class ServerSettings:
    host: str
    port: int
    production: bool

    @classmethod
    def from_kwargs(cls, kwargs: ServerConfigArgs, /) -> ServerSettings:
        return cls(
            kwargs.get("host") or "localhost",
            kwargs.get("port") or 5000,
            kwargs.get("production") or False,
        )


def run_uvicorn(app: BaseApp, settings: ServerSettings) -> None:
    """
    Run the app using the ``uvicorn`` library.
    """
    import uvicorn

    uvicorn.run(app.asgi(), host=settings.host, port=settings.port)


def run_hypercorn(app: BaseApp, settings: ServerSettings) -> None:
    """
    Run the app using the ``hypercorn`` library.
    """
    import asyncio

    import hypercorn
    from hypercorn.asyncio import serve

    config = hypercorn.Config()
    config.bind = [f"{settings.host}:{settings.port}"]
    asyncio.run(serve(app.asgi(), config))  # type: ignore


def run_daphne(app: BaseApp, settings: ServerSettings) -> None:
    """
    Run the app using the ``daphne`` library.
    """
    from daphne.endpoints import build_endpoint_description_strings
    from daphne.server import Server

    endpoints = build_endpoint_description_strings(
        host=settings.host,
        port=settings.port,
    )
    server = Server(app.asgi(), endpoints=endpoints)
    server.run()


def run_gunicorn(app: BaseApp, settings: ServerSettings) -> None:
    """
    Run the app using the ``gunicorn`` library.
    """
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

    runner = GunicornRunner(
        app.wsgi(), {"bind": f"{settings.host}:{settings.port}"}
    )
    runner.run()


def run_werkzeug(app: BaseApp, settings: ServerSettings) -> None:
    """
    Run the app using the ``werkzeug`` library.
    """
    from werkzeug.serving import run_simple

    run_simple(settings.host, settings.port, app.wsgi())


def run_wsgiref(app: BaseApp, settings: ServerSettings) -> None:
    """
    Run the app using the built-in :mod:`wsgiref` module.
    """
    from wsgiref.simple_server import make_server

    with make_server(settings.host, settings.port, app.wsgi()) as server:
        server.serve_forever()


StartServer: TypeAlias = Callable[["BaseApp", ServerSettings], None]

ALL_SERVERS: MutableMapping[str, StartServer] = {
    "uvicorn": run_uvicorn,
    "hypercorn": run_hypercorn,
    "daphne": run_daphne,
    "gunicorn": run_gunicorn,
    "werkzeug": run_werkzeug,
    "wsgiref": run_wsgiref,
}


def run_app_on_any_server(
    app: BaseApp, **kwargs: Unpack[ServerConfigArgs]
) -> None:
    """
    Run the app on the nearest available ASGI or WSGI server.

    This will always succeed, as it will fall back to the standard
    :mod:`wsgiref` module if no other server is installed.
    """
    settings = ServerSettings.from_kwargs(kwargs)
    hint = kwargs.get("server_hint")
    if hint is not None:
        try:
            start_server = ALL_SERVERS[hint]
        except KeyError as key_error:
            raise BadServerError(
                f"{hint!r} is not a known server"
            ) from key_error

        try:
            return start_server(app, settings)
        except ImportError as error:
            raise BadServerError(f"{hint} is not installed") from error

    # I'm not sure what Ruff is complaining about here
    for start_server in ALL_SERVERS.values():
        with suppress(ImportError):
            return start_server(app, settings)
