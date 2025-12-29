from __future__ import annotations

from collections.abc import Awaitable, Callable, MutableMapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeAlias

from view.exceptions import InvalidType, ViewError
from view.status_codes import HTTPError, status_exception

if TYPE_CHECKING:
    from view.core.request import Method
    from view.core.response import ResponseLike

__all__ = "Route", "Router"


RouteView: TypeAlias = Callable[[], "ResponseLike | Awaitable[ResponseLike]"]


@dataclass(slots=True, frozen=True)
class Route:
    """
    Dataclass representing a route in a router.
    """

    view: RouteView
    path: str
    method: Method

    def __truediv__(self, other: object) -> str:
        if not isinstance(other, str):
            return NotImplemented

        path = f"{self.path}/{other}"
        return normalize_route(path)


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


class DuplicateRoute(ViewError):
    """
    The router found multiple views for the same route.

    Generally, this means that a typo is present, or perhaps the user
    misunderstood something about route normalization. For example, "/" and ""
    are equivalent to the router.
    """


SubRouter: TypeAlias = Callable[[str], "FoundRoute"]


@dataclass(slots=True)
class PathNode:
    """
    A node in the "path tree".
    """

    name: str
    routes: MutableMapping[Method, Route] = field(default_factory=dict)
    children: MutableMapping[str, PathNode] = field(default_factory=dict)
    path_parameter: PathNode | None = None
    subrouter: SubRouter | None = None

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
            raise DuplicateRoute(
                f"Path parameter {name} is in the same place as"
                f" {self.path_parameter.name}, but with a different name",
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
    path_parameters: MutableMapping[str, str]


@dataclass(slots=True, frozen=True)
class Router:
    """
    Standard router that supports error and route lookups.
    """

    error_views: MutableMapping[type[HTTPError], RouteView] = field(
        default_factory=dict
    )
    parent_node: PathNode = field(default_factory=lambda: PathNode(name=""))

    def _get_node_for_path(self, path: str) -> PathNode:
        path = normalize_route(path)
        parent_node = self.parent_node
        parts = path.split("/")

        for part in parts:
            if is_path_parameter(part):
                parent_node = parent_node.parameter(extract_path_parameter(part))
            else:
                parent_node = parent_node.next(part)

        return parent_node

    def push_route(self, view: RouteView, path: str, method: Method) -> Route:
        """
        Register a view with the router.
        """

        node = self._get_node_for_path(path)
        if node.routes.get(method) is not None:
            raise DuplicateRoute(
                f"The route {path!r} was already used for method {method.value}"
            )

        route = Route(view=view, path=path, method=method)
        node.routes[method] = route
        return route

    def push_subrouter(self, subrouter: SubRouter, path: str) -> None:
        """
        Register a subrouter that will be used to delegate parsing when nothing
        else is found.
        """

        node = self._get_node_for_path(path)
        if node.subrouter is not None:
            raise DuplicateRoute(f"The route {path!r} already has a subrouter")

        node.subrouter = subrouter

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
            raise InvalidType((int, type), error)

        self.error_views[error_type] = view

    def lookup_route(self, path: str, method: Method, /) -> FoundRoute | None:
        """
        Look up the view for the route.
        """
        path_parameters: dict[str, str] = {}
        assert normalize_route(path) == path, "Request() should've normalized the route"

        parent_node = self.parent_node
        parts = path.split("/")

        for index, part in enumerate(parts):
            node = parent_node.children.get(part)
            if node is None:
                node = parent_node.path_parameter
                if node is None:
                    if parent_node.subrouter is not None:
                        remaining = "/".join(parts[index:])
                        return parent_node.subrouter(remaining)

                    # This route doesn't exist
                    return

                path_parameters[node.name] = part

            parent_node = node

        final_route: Route | None = parent_node.routes.get(method)
        if final_route is None:
            if parent_node.subrouter is not None:
                return parent_node.subrouter("/")
            return None

        return FoundRoute(final_route, path_parameters)

    def lookup_error(self, error: type[HTTPError], /) -> RouteView | None:
        """
        Look up the error view for the given HTTP error.
        """
        return self.error_views.get(error)
