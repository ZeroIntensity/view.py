from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import (Any, Callable, ClassVar, Generic, NamedTuple, Protocol,
                    TypeVar)


class BodyLike(Protocol):
    __view_body__: ClassVar[dict[str, ValueType]]


ValueType = BodyLike | str | int | dict[str, "ValueType"] | bool | float


class Method(Enum):
    NOTSET = 0
    GET = 1
    POST = 2


V = TypeVar("V", bound="ValueType")

ValidatorResult = bool | tuple[bool, str]
Validator = Callable[[V], ValidatorResult]


class RouteInput(NamedTuple, Generic[V]):
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
    doc: str | None = None
    cache_rate: int = -1


RouteOrCallable = Route | Callable[..., Any]


def _ensure_route(r: RouteOrCallable) -> Route:
    if isinstance(r, Route):
        return r
    return Route(None, Method.NOTSET, {}, {}, None)


def _method(
    r: RouteOrCallable,
    path: str,
    doc: str | None,
    method: Method,
) -> Route:
    route = _ensure_route(r)
    route.method = method
    route.path = path
    if doc:
        route.doc = doc

    return route


def get(path: str, doc: str | None = None):
    def inner(r: RouteOrCallable) -> Route:
        return _method(r, path, doc, Method.GET)

    return inner


def post(path: str, doc: str | None = None):
    def inner(r: RouteOrCallable) -> Route:
        return _method(r, path, doc, Method.POST)

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
