from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Awaitable, Callable, TypeAlias

from view.status_codes import HTTPError, status_exception

if TYPE_CHECKING:
    from view.request import Method
    from view.response import ResponseLike

__all__ = "Route", "Router"


RouteView: TypeAlias = Callable[[], "ResponseLike" | Awaitable["ResponseLike"]]


@dataclass(slots=True, frozen=True)
class Route:
    """
    Dataclass representing a route in a router.
    """

    view: RouteView
    path: str
    method: Method


@dataclass(slots=True, frozen=True)
class Router:
    """
    Standard router that supports error and route lookups.
    """

    route_views: dict[str, Route] = field(default_factory=dict)
    error_views: dict[type[HTTPError], RouteView] = field(default_factory=dict)

    def push_route(self, view: RouteView, path: str, method: Method) -> None:
        """
        Register a view with the router.
        """
        self.route_views[path] = Route(view=view, path=path, method=method)

    def push_error(self, error: int | type[HTTPError], view: RouteView) -> None:
        """
        Register an error view with the router.
        """
        error_type: type[HTTPError]
        if isinstance(error, int):
            error_type = status_exception(error)
        elif issubclass(error, HTTPError):
            error_type = error
        else:
            raise TypeError(f"expected a status code or type, but got {error!r}")

        self.error_views[error_type] = view

    def lookup_route(self, path: str, /) -> Route | None:
        """
        Look up the view for the route.
        """
        return self.route_views.get(path)

    def lookup_error(self, error: type[HTTPError], /) -> RouteView | None:
        """
        Look up the error view for the given HTTP error.
        """
        return self.error_views.get(error)
