from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Awaitable, Callable, TypeAlias, TypeVar

from view.status_codes import HTTPError, status_exception

from view.response import ResponseLike

__all__ = "Method", "Route", "Router"


class Method(StrEnum):
    GET = auto()
    POST = auto()
    PUT = auto()
    PATCH = auto()
    DELETE = auto()
    CONNECT = auto()
    OPTIONS = auto()
    TRACE = auto()
    HEAD = auto()


RouteView: TypeAlias = Callable[[], ResponseLike | Awaitable[ResponseLike]]


@dataclass(slots=True, frozen=True)
class Route:
    view: RouteView
    path: str
    method: Method


class BaseRouter(ABC):
    @abstractmethod
    def lookup_route(self, path: str, /) -> Route | None: ...

    @abstractmethod
    def lookup_error(self, error: type[HTTPError], /) -> RouteView: ...


class Router(BaseRouter):
    def __init__(self) -> None:
        self.route_views: dict[str, Route] = {}
        self.error_views: dict[type[HTTPError], RouteView] = {}

    def push_route(self, view: RouteView, path: str, method: Method) -> None:
        self.route_views[path] = Route(view=view, path=path, method=method)

    def push_error(self, error: int | type[HTTPError], view: RouteView) -> None:
        error_type: type[HTTPError]
        if isinstance(error, int):
            error_type = status_exception(error)
        elif issubclass(error, HTTPError):
            error_type = error
        else:
            raise TypeError(f"expected a status code or type, but got {error!r}")

        self.error_views[error_type] = view

    def lookup_route(self, path: str, /) -> Route | None:
        return self.route_views.get(path)

    def lookup_error(self, error: type[HTTPError], /) -> RouteView:
        return self.error_views.get(error) or self.default_error(error)

    def default_error(self, error: type[HTTPError]) -> RouteView:
        """
        Get the default error view for a given HTTP error.
        """

        def inner():
            return f"Error {error.status_code}"

        return inner
