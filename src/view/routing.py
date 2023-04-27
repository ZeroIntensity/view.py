from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generic, TypeVar

from typing_extensions import Concatenate, ParamSpec

from .typing import Context, Validator, ValueType, ViewResponse, ViewRoute


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


P = ParamSpec("P")
T = TypeVar("T", bound="ViewResponse")


@dataclass
class Route(Generic[P, T]):
    func: Callable[P, T]
    path: str | None
    method: Method
    inputs: list[RouteInput]
    callable: ViewRoute
    doc: str | None = None
    cache_rate: int = -1
    errors: dict[int, ViewRoute] | None = None
    pass_context: bool = False

    def error(self, status_code: int):
        def wrapper(handler: ViewRoute):
            if not self.errors:
                self.errors = {}

            self.errors[status_code] = handler
            return handler

        return wrapper

    def __repr__(self):
        return f"route for {self.path or '<unknown at this time>'}"

    __str__ = __repr__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*args, **kwargs)


RouteOrCallable = Route[P, T] | ViewRoute[P, T]


def _ensure_route(r: RouteOrCallable[P, T]) -> Route[P, T]:
    if isinstance(r, Route):
        return r

    return Route(r, None, Method.GET, [], r)


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

        return _method(r, path_or_route, doc, method)

    if not path_or_route:
        return inner

    if isinstance(path_or_route, str):
        return inner

    return inner


Path = Callable[[str | None | RouteOrCallable[P, T]]]


def get(
    path_or_route: str | None | RouteOrCallable[P, T] = None,
    doc: str | None = None,
) -> Path[P, T]:
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
) -> Callable[[RouteOrCallable[Concatenate[V, P]]], Route]:
    def inner(r: RouteOrCallable[Concatenate[V, P]]) -> Route:
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
