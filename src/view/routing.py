from __future__ import annotations

import builtins
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, Type, TypeVar, Union

from typing_extensions import ParamSpec

from ._util import LoadChecker, make_hint
from .exceptions import MistakeError
from .typing import Validator, ValueType, ViewResponse, ViewRoute

__all__ = (
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "query",
    "body",
    "route_types",
    "cache",
    "BodyParam",
)

PART = re.compile(r"{(((\w+)(: *(\w+)))|(\w+))}")


class Method(Enum):
    GET = 1
    POST = 2
    DELETE = 3
    PATCH = 4
    PUT = 5
    OPTIONS = 6


V = TypeVar("V", bound="ValueType")


@dataclass
class BodyParam(Generic[V]):
    types: type[V] | list[type[V]] | tuple[type[V], ...]
    default: V


@dataclass
class RouteInput(Generic[V]):
    name: str
    is_body: bool
    tp: tuple[type[V], ...]
    default: V | None | _NoDefaultType
    doc: str | None
    validators: list[Validator[V]]


P = ParamSpec("P")
T = TypeVar("T", bound="ViewResponse")


@dataclass
class Part(Generic[V]):
    name: str
    type: type[V] | None


@dataclass
class Route(Generic[P, T], LoadChecker):
    func: Callable[P, T]
    path: str | None
    method: Method
    inputs: list[RouteInput]
    callable: ViewRoute
    doc: str | None = None
    cache_rate: int = -1
    errors: dict[int, ViewRoute] | None = None
    pass_context: bool = False
    extra_types: dict[str, Any] = field(default_factory=dict)
    parts: list[str | Part[Any]] = field(default_factory=list)

    def error(self, status_code: int):
        def wrapper(handler: ViewRoute):
            if not self.errors:
                self.errors = {}

            self.errors[status_code] = handler
            return handler

        return wrapper

    def __repr__(self):
        return f"Route({self.method.name}(\"{self.path or '/???'}\"))"  # noqa

    __str__ = __repr__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*args, **kwargs)


RouteOrCallable = Union[Route[P, T], ViewRoute[P, T]]


def _ensure_route(r: RouteOrCallable[..., Any]) -> Route[..., Any]:
    if isinstance(r, Route):
        return r

    return Route(r, None, Method.GET, [], r)


def route_types(
    r: RouteOrCallable[P, T],
    data: type[Any] | tuple[type[Any]] | dict[str, Any],
) -> Route[P, T]:
    route = _ensure_route(r)
    if isinstance(data, tuple):
        for i in data:
            route.extra_types[i.__name__] = i
    elif isinstance(data, dict):
        route.extra_types.update(data)
    elif isinstance(data, type):
        route.extra_types[data.__name__] = data
    else:
        raise TypeError(
            "expected type, tuple of tuples,"
            f" or a dict, got {type(data).__name__}"
        )

    return route


def _method(
    r: RouteOrCallable[P, T],
    raw_path: str | None,
    doc: str | None,
    method: Method,
) -> Route[P, T]:
    route = _ensure_route(r)
    route.method = method
    util_path = raw_path or "/"

    if not util_path.startswith("/"):
        raise MistakeError(
            "paths must started with a slash",
            hint=make_hint(
                f'This should be "/{util_path}" instead', back_lines=2
            ),
        )

    if util_path.endswith("/") and (len(util_path) != 1):
        raise MistakeError(
            "paths must not end with a slash",
            hint=make_hint(
                f'This should be "{util_path[:-1]}" instead', back_lines=2
            ),
        )

    if "{" in util_path:
        assert raw_path
        parts: list[str | Part] = []

        for index, i in enumerate(util_path[1:].split("/")):
            match = PART.match(i)

            if not match:
                parts.append("/" + i)
                continue

            if index == 0:
                raise MistakeError(
                    "first part must not be a path parameter",
                    hint=make_hint("Not allowed!", back_lines=2),
                )

            if match.group(6):
                parts.append(Part("/" + match.group(6), None))
            else:
                parts.append(
                    Part(
                        match.group(3),
                        {
                            **globals(),
                            **route.extra_types,
                            **{i: getattr(builtins, i) for i in dir(builtins)},
                        }[match.group(5)],
                    )
                )

        route.parts = parts
        route.path = None
    else:
        route.path = raw_path

    if doc:
        route.doc = doc

    return route


Path = Callable[[RouteOrCallable[P, T]], Route[P, T]]


def _method_wrapper(
    path_or_route: str | None | RouteOrCallable[P, T],
    doc: str | None,
    method: Method,
) -> Path[P, T]:
    def inner(r: RouteOrCallable[P, T]) -> Route[P, T]:
        if (not isinstance(path_or_route, str)) and path_or_route:
            raise TypeError(f"{path_or_route!r} is not a string")

        return _method(r, path_or_route, doc, method)

    if not path_or_route:
        return inner

    if isinstance(path_or_route, str):
        return inner

    return inner


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


class _NoDefault:
    __VIEW_NODEFAULT__ = 1


_NoDefaultType = Type[_NoDefault]


def query(
    name: str,
    *tps: type[V],
    doc: str | None = None,
    default: V | None | _NoDefaultType = _NoDefault,
):
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.inputs.append(RouteInput(name, False, tps, default, doc, []))
        return route

    return inner


def body(
    name: str,
    *tps: type[V],
    doc: str | None = None,
    default: V | None | _NoDefaultType = _NoDefault,
):
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.inputs.append(RouteInput(name, True, tps, default, doc, []))
        return route

    return inner


def cache(amount: int):
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.cache_rate = amount
        return route

    return inner
