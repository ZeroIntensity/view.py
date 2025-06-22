from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Awaitable, Callable, TypeAlias, TypeVar

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


@dataclass(slots=True, frozen=True)
class Route:
    handler: RouteHandler
    path: str
    method: Method


class BaseRouter(ABC):
    @abstractmethod
    def lookup_route(self, path: str, /) -> Route | None: ...

    @abstractmethod
    def lookup_error(self, error: type[HTTPError], /) -> RouteHandler: ...


class Router(BaseRouter):
    def __init__(self) -> None:
        self.route_handlers: dict[str, Route] = {}
        self.error_handlers: dict[type[HTTPError], RouteHandler] = {}

    def push_route(self, handler: RouteHandler, path: str, method: Method) -> None:
        self.route_handlers[path] = Route(handler=handler, path=path, method=method)

    def push_error(self, error: int | type[HTTPError], handler: RouteHandler) -> None:
        error_type: type[HTTPError]
        if isinstance(error, int):
            error_type = status_exception(error)
        elif issubclass(error, HTTPError):
            error_type = error
        else:
            raise TypeError(f"expected a status code or type, but got {error!r}")

        self.error_handlers[error_type] = handler

    def lookup_route(self, path: str, /) -> Route | None:
        return self.route_handlers.get(path)

    def lookup_error(self, error: type[HTTPError], /) -> RouteHandler:
        return self.error_handlers.get(error) or self.default_error(error)

    def default_error(self, error: type[HTTPError]) -> RouteHandler:
        """
        Get the default error handler for a given HTTP error.
        """

        def inner():
            return f"Error {error.status_code}"

        return inner
