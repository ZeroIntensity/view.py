from __future__ import annotations

from ._util import run_path
from .exceptions import DuplicateRouteError, InvalidRouteError
from .routing import (Callable, Method, Route, RouteOrCallable, delete, get,
                      options, patch, post, put)
from .routing import route as route_impl
from .typing import StrMethod, ViewRoute

__all__ = "RouteInput", "path"

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


def path(
    target: str,
    path_or_function: str | ViewRoute | Route,
    method: Method | StrMethod = "GET",
    *inputs: RouteInput,
) -> Route:
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

    if isinstance(method, str):
        method = method.lower()  # type: ignore

    if method in _STR_MAPPINGS:
        method_enum: Method = _STR_MAPPINGS[method]
    else:
        method_enum: Method = method  # type: ignore

    func = _FUNC_MAPPINGS[method_enum]

    if isinstance(route, Route):
        if not route.method:
            route_obj = route_impl(target)(route)
            route_obj.method_list = route.method_list
        elif route.method != method_enum:
            method_enum = route.method

        func = _FUNC_MAPPINGS[method_enum]
        route_obj = func(target)(route)
    else:
        route_obj = func(target)(route)

    for i in inputs:
        i(route_obj)

    return route_obj
