from __future__ import annotations
from enum import Enum, auto
from typing import Awaitable, Callable, TypeAlias, TypeVar
from dataclasses import dataclass
from status_codes import HTTPError, status_exception
from view.response import ResponseLike

__all__ = "Method", "Route", "Router"


class Method(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    PATCH = auto()
    DELETE = auto()
    CONNECT = auto()
    OPTIONS = auto()
    TRACE = auto()
    HEAD = auto()



RouteHandler: TypeAlias = Callable[[], ResponseLike | Awaitable[ResponseLike]]
RouteHandlerVar = TypeVar("RouteHandlerVar", bound=RouteHandler)
RouteDecorator: TypeAlias = Callable[[RouteHandlerVar], RouteHandlerVar]

@dataclass(slots=True, frozen=True)
class Route:
    handler: RouteHandler
    path: str
    method: Method

class Router:
    def __init__(self) -> None:
        self.routes: dict[str, Route] = {}
        self.error_handlers: dict[type[HTTPError], RouteHandler] = {}

    def push_route(self, handler: RouteHandler, path: str, method: Method) -> None:
        self.routes[path] = Route(handler=handler, path=path, method=method)

    def lookup_route(self, path: str) -> Route | None:
        return self.routes.get(path)

    def route(self, path: str, /, *, method: Method) -> RouteDecorator:
        """
        Decorator interface for adding a route to the app.
        """

        def decorator(function: RouteHandlerVar, /) -> RouteHandlerVar:
            self.push_route(function, path, method)
            return function

        return decorator

    def get(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.GET)

    def post(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.POST)

    def put(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.PUT)

    def patch(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.PATCH)

    def delete(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.DELETE)

    def connect(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.CONNECT)

    def options(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.OPTIONS)

    def trace(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.TRACE)

    def head(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.HEAD)

    def error(self, status: int | type[HTTPError]) -> RouteDecorator:
        error_type: type[HTTPError]
        if isinstance(status, int):
            error_type = status_exception(status)
        elif issubclass(status, HTTPError):
            error_type = status
        else:
            raise TypeError(f"expected a status code or type, but got {status!r}")
        
        def decorator(function: RouteHandlerVar) -> RouteHandlerVar:
            self.error_handlers[error_type] = function
            return function

        return decorator
