from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

from .typing import Validator, ValueType, ViewRoute


class Method(Enum):
    GET = 1
    POST = 2
    DELETE = 3
    PATCH = 4
    PUT = 5
    OPTIONS = 6


V = TypeVar("V", bound="ValueType")


@dataclass
class RouteInput(Generic[V]):
    name: str
    is_body: bool
    tp: type[V] | None
    default: V | None
    doc: str | None
    validators: list[Validator[V]]


@dataclass
class Route:
    path: str | None
    method: Method
    inputs: list[RouteInput]
    callable: ViewRoute
    doc: str | None = None
    cache_rate: int = -1


RouteOrCallable = Route | ViewRoute


def _ensure_route(r: RouteOrCallable) -> Route:
    if isinstance(r, Route):
        return r
    return Route(None, Method.GET, [], r)


def _method(
    r: RouteOrCallable,
    path: str | None,
    doc: str | None,
    method: Method,
) -> Route:
    route = _ensure_route(r)
    route.method = method
    route.path = path

    if doc:
        route.doc = doc

    return route


def _method_wrapper(
    path_or_route: str | None | RouteOrCallable,
    doc: str | None,
    method: Method,
):
    def inner(r: RouteOrCallable) -> Route:
        if not isinstance(path_or_route, str):
            raise TypeError(f"{path_or_route!r} is not a string")
        return _method(r, path_or_route, doc, Method.GET)

    if not path_or_route:
        return inner

    if isinstance(path_or_route, str):
        return inner

    return inner


def get(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
):
    return _method_wrapper(path_or_route, doc, Method.GET)


def post(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
):
    return _method_wrapper(path_or_route, doc, Method.POST)


def patch(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
):
    return _method_wrapper(path_or_route, doc, Method.PATCH)


def put(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
):
    return _method_wrapper(path_or_route, doc, Method.PUT)


def delete(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
):
    return _method_wrapper(path_or_route, doc, Method.DELETE)


def options(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
):
    return _method_wrapper(path_or_route, doc, Method.OPTIONS)


def query(
    name: str,
    tp: type[V] | None = None,
    doc: str | None = None,
    *,
    default: V | None = None,
):
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.inputs.append(RouteInput(name, False, tp, default, doc, []))
        return route

    return inner


def body(
    name: str,
    tp: type[V] | None = None,
    doc: str | None = None,
    *,
    default: V | None = None,
):
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.inputs.append(RouteInput(name, True, tp, default, doc, []))
        return route

    return inner


def cache(amount: int):
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.cache_rate = amount
        return route

    return inner
