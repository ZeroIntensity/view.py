"""
view.py patterns API

This contains the `path()` function, which acts as the logic for the Django-like `patterns` loader.
"""

from __future__ import annotations

from ._util import run_path
from .exceptions import DuplicateRouteError, InvalidRouteError
from .routing import (
    Callable,
    Method,
    Route,
    RouteOrCallable,
    delete,
    get,
    options,
    patch,
    post,
    put,
)
from .routing import route as route_impl
from .typing import StrMethod, ViewRoute

__all__ = "RouteInput", "path"
_Get = None

_FUNC_MAPPINGS = {
    Method.GET: get,
    Method.POST: post,
    Method.PUT: put,
    Method.PATCH: patch,
    Method.DELETE: delete,
    Method.OPTIONS: options,
}

_STR_MAPPINGS = {
    "get": Method.GET,
    "post": Method.POST,
    "put": Method.PUT,
    "patch": Method.PATCH,
    "delete": Method.DELETE,
    "options": Method.OPTIONS,
}

RouteInput = Callable[[RouteOrCallable], Route]


def _get_method_enum(method: StrMethod | None | Method) -> Method:
    if isinstance(method, str):
        method = method.lower()  # type: ignore

    if method in _STR_MAPPINGS:
        method_enum: Method = _STR_MAPPINGS[method]  # type: ignore
    else:
        method_enum: Method = method or Method.GET  # type: ignore

    return method_enum


def path(
    target: str,
    path_or_function: str | ViewRoute | Route,
    *inputs: RouteInput,
    method: Method | StrMethod | None = _Get,
) -> Route:
    """
    Function to generate a `Route` object using Django-like routing.

    Args:
        target: URL path of the route.
        path_or_function: Path to a route, a function representing a route, or a Route object (meaning a function was decorated with `get()` or some other router function).
        inputs: All route inputs, e.g. `query()` or `body()`. Note that route inputs decorated on the function itself are automatically transferred.
        method: Method of the route. `GET` by default.

    Raises:
        DuplicateRouteError: Parameter `target` is a string specifying a module path, and it contains multiple `Route` objects.
        InvalidRouteError: `target` is a string specifying a module that has no `Route` objects.

    Example:
        ```py
        # urls.py
        from view import path, body
        from .routes import index, create_account

        patterns = [
            path("/", index),
            path(
                "/create",
                create_account,
                body("username", str),
                body("password", str),
                method="POST"
            )
        ]
        ```
    """
    if isinstance(path_or_function, str):
        mod = run_path(path_or_function)
        route: Route | ViewRoute | None = None

        for v in mod.values():
            if isinstance(v, Route) or callable(v):
                if route:
                    raise DuplicateRouteError(
                        f"multiple routes found in {path_or_function}"
                    )

                route = v

        if not route:
            raise InvalidRouteError(f"no route in {path_or_function}")
    else:
        route = path_or_function

    if not isinstance(route, Route):
        method_enum = _get_method_enum(method)
        func = _FUNC_MAPPINGS[method_enum]
        route_obj: Route = func(target)(route)
    else:
        if not route.method:
            route_obj = route_impl(target)(route)
            route_obj.method_list = route.method_list
        else:
            method_enum = _get_method_enum(method or route.method)
            func = _FUNC_MAPPINGS[method_enum]
            route_obj = func(target)(route)

    for i in inputs:
        i(route_obj)

    return route_obj
