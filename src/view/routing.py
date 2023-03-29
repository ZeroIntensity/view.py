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
    tp: type[V] | None
    default: V | None
    doc: str | None
    validators: list[Validator[V]]


@dataclass
class Route:
    path: str | None
    method: Method
    query: dict[str, RouteInput]
    body: dict[str, RouteInput]
    callable: ViewRoute
    doc: str | None = None
    cache_rate: int = -1


RouteOrCallable = Route | ViewRoute


def _ensure_route(r: RouteOrCallable) -> Route:
    if isinstance(r, Route):
        return r
    return Route(None, Method.GET, {}, {}, r)


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


def get(path: str | None = None, doc: str | None = None):
    def inner(r: RouteOrCallable) -> Route:
        return _method(r, path, doc, Method.GET)

    return inner


def post(path: str | None = None, doc: str | None = None):
    def inner(r: RouteOrCallable) -> Route:
        return _method(r, path, doc, Method.POST)

    return inner


def put(path: str | None = None, doc: str | None = None):
    def inner(r: RouteOrCallable) -> Route:
        return _method(r, path, doc, Method.PUT)

    return inner


def patch(path: str | None = None, doc: str | None = None):
    def inner(r: RouteOrCallable) -> Route:
        return _method(r, path, doc, Method.PATCH)

    return inner


def delete(path: str | None = None, doc: str | None = None):
    def inner(r: RouteOrCallable) -> Route:
        return _method(r, path, doc, Method.DELETE)

    return inner


def options(path: str | None = None, doc: str | None = None):
    def inner(r: RouteOrCallable) -> Route:
        return _method(r, path, doc, Method.OPTIONS)

    return inner


def query(
    name: str,
    tp: type[V] | None = None,
    doc: str | None = None,
    *,
    default: V | None = None,
):
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.query[name] = RouteInput(tp, default, doc, [])
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
        route.body[name] = RouteInput(tp, default, doc, [])
        return route

    return inner


def cache(amount: int):
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.cache_rate = amount
        return route

    return inner
