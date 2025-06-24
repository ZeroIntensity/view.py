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


def normalize_route(route: str, /) -> str:
    """
    Format a route (without any leading URL) into a common style.
    """
    if route in {"", "/"}:
        return "/"

    route = route.rstrip("/")
    if not route.startswith("/"):
        route = "/" + route

    return route


@dataclass(slots=True)
class PathNode:
    """
    A node in the "path tree".
    """

    name: str
    routes: dict[Method, Route] = field(default_factory=dict)
    children: dict[str, PathNode] = field(default_factory=dict)
    path_parameter: PathNode | None = field(default=None)

    def parameter(self, name: str) -> PathNode:
        """
        Mark this node as having a path parameter (if not already), and
        return the path parameter node.
        """
        if self.path_parameter is None:
            next_node = PathNode(name=name)
            self.path_parameter = next_node
            return next_node
        if __debug__ and name != self.path_parameter.name:
            raise ValueError(
                f"path parameter {name} in the same place as {self.path_parameter.name} but with a different name",
            )
        return self.path_parameter

    def next(self, part: str) -> PathNode:
        """
        Get the next node for the given path part, creating it if it doesn't
        exist.
        """
        node = self.children.get(part)
        if node is not None:
            return node

        new_node = PathNode(name=part)
        self.children[part] = new_node
        return new_node


def is_path_parameter(part: str) -> bool:
    """
    Is this part a path parameter?
    """
    return part.startswith("{") and part.endswith("}")


def extract_path_parameter(part: str) -> str:
    """
    Extract the name of a path parameter from a string given by the user
    in a route string.
    """
    return part[1 : len(part) - 1]


@dataclass(slots=True, frozen=True)
class FoundRoute:
    """
    Dataclass representing a route that was looked up by the router
    for a given path.
    """

    route: Route
    path_parameters: dict[str, str]


@dataclass(slots=True, frozen=True)
class Router:
    """
    Standard router that supports error and route lookups.
    """

    error_views: dict[type[HTTPError], RouteView] = field(default_factory=dict)
    parent_node: PathNode = field(default_factory=lambda: PathNode(name=""))

    def push_route(self, view: RouteView, path: str, method: Method) -> None:
        """
        Register a view with the router.
        """
        path = normalize_route(path)
        parent_node = self.parent_node
        parts = path.split("/")
        route = Route(view=view, path=path, method=method)

        for part in parts:
            if is_path_parameter(part):
                parent_node = parent_node.parameter(extract_path_parameter(part))
            else:
                parent_node = parent_node.next(part)

        if parent_node.routes.get(method) is not None:
            raise RuntimeError(f"the route {path!r} was already used")

        parent_node.routes[method] = route

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

    def lookup_route(self, path: str, method: Method, /) -> FoundRoute | None:
        """
        Look up the view for the route.
        """
        path_parameters: dict[str, str] = {}
        assert normalize_route(path) == path, "Request() should've normalized the route"

        parent_node = self.parent_node
        parts = path.split("/")

        for part in parts:
            node = parent_node.children.get(part)
            if node is None:
                node = parent_node.path_parameter
                if node is None:
                    # This route doesn't exist
                    return None

                path_parameters[node.name] = part

            parent_node = node

        final_route: Route | None = parent_node.routes.get(method)
        if final_route is None:
            return None

        return FoundRoute(final_route, path_parameters)

    def lookup_error(self, error: type[HTTPError], /) -> RouteView | None:
        """
        Look up the error view for the given HTTP error.
        """
        return self.error_views.get(error)
