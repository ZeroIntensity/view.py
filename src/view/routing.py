from __future__ import annotations

import builtins
import inspect
import re
from contextlib import suppress
from dataclasses import dataclass, field
from enum import Enum
from typing import (Any, Callable, Generic, Iterable, Literal, Type, TypeVar,
                    Union)

from ._util import LoadChecker, make_hint
from .exceptions import InvalidRouteError, MistakeError
from .typing import (Middleware, StrMethod, Validator, ValueType, ViewResponse,
                     ViewRoute)

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
    "BodyParam",
    "context",
    "route"
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


@dataclass
class Part(Generic[V]):
    name: str
    type: type[V] | None


RouteData = Literal[1]

@dataclass
class Route(LoadChecker):
    """Standard Route Wrapper"""

    func: Callable[..., ViewResponse]
    path: str | None
    method: Method | None
    inputs: list[RouteInput | RouteData]
    doc: str | None = None
    cache_rate: int = -1
    errors: dict[int, ViewRoute] | None = None
    extra_types: dict[str, Any] = field(default_factory=dict)
    parts: list[str | Part[Any]] = field(default_factory=list)
    middleware_funcs: list[Middleware] = field(default_factory=list)
    method_list: list[Method] | None = None

    def error(self, status_code: int):
        def wrapper(handler: ViewRoute):
            if not self.errors:
                self.errors = {}

            self.errors[status_code] = handler
            return handler

        return wrapper

    def middleware(self, func_or_none: Middleware | None = None):
        """Define a middleware function for the route."""
        def inner(func: Middleware):
            self.middleware_funcs.append(func)
        
        if func_or_none:
            return inner(func_or_none)

        return inner

    def __repr__(self):
        return f"Route({self.method.name if self.method else 'ANY_METHOD'}(\"{self.path or '/???'}\"))"  # noqa

    __str__ = __repr__

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)


RouteOrCallable = Union[Route, ViewRoute]


def _ensure_route(r: RouteOrCallable) -> Route:
    if isinstance(r, Route):
        return r

    return Route(r, None, Method.GET, [])


def route_types(
    r: RouteOrCallable,
    data: type[Any] | tuple[type[Any]] | dict[str, Any],
) -> Route:
    route = _ensure_route(r)
    if isinstance(data, tuple):
        for i in data:
            route.extra_types[i.__name__] = i
    elif isinstance(data, dict):
        route.extra_types.update(data)
    elif isinstance(data, type):
        route.extra_types[data.__name__] = data
    else:
        raise InvalidRouteError(
            "expected type, tuple of tuples," f" or a dict, got {type(data).__name__}"
        )

    return route


def _method(
    r: RouteOrCallable,
    raw_path: str | None,
    doc: str | None,
    method: Method | None,
    cache_rate: int,
    *,
    method_list: list[Method] | None = None
) -> Route:
    route = _ensure_route(r)
    route.method = method
    route.cache_rate = cache_rate
    route.method_list = method_list
    util_path = raw_path or "/"

    if not util_path.startswith("/"):
        raise MistakeError(
            "paths must started with a slash",
            hint=make_hint(f'This should be "/{util_path}" instead', back_lines=2),
        )

    if util_path.endswith("/") and (len(util_path) != 1):
        raise MistakeError(
            "paths must not end with a slash",
            hint=make_hint(f'This should be "{util_path[:-1]}" instead', back_lines=2),
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
    else:
        route.doc = route.func.__doc__

    return route


Path = Callable[[RouteOrCallable], Route]


def _method_wrapper(
    path_or_route: str | None | RouteOrCallable,
    doc: str | None,
    method: Method | None,
    cache_rate: int,
    *,
    method_list: list[Method] | None = None
) -> Path:
    def inner(r: RouteOrCallable) -> Route:
        if (not isinstance(path_or_route, str)) and path_or_route:
            raise TypeError(f"{path_or_route!r} is not a string")

        return _method(r, path_or_route, doc, method, cache_rate, method_list=method_list)

    if not path_or_route:
        return inner

    if isinstance(path_or_route, str):
        return inner

    return inner


def get(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
    *,
    cache_rate: int = -1,
) -> Path:
    """Add a GET route.

    Args:
        path_or_route: The path to this route, or the route itself.
        doc: The description of the route to be used in documentation.
        cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

    Example:
        ```py
        from view import get

        @get("/")
        async def index():
            return "Hello, view.py!"
        ```
    """
    return _method_wrapper(path_or_route, doc, Method.GET, cache_rate)


def post(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
    *,
    cache_rate: int = -1,
) -> Path:
    """Add a POST route.

    Args:
        path_or_route: The path to this route, or the route itself.
        doc: The description of the route to be used in documentation.
        cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

    Example:
        ```py
        from view import post

        @post("/")
        async def index():
            return "Hello, view.py!"
        ```
    """
    return _method_wrapper(path_or_route, doc, Method.POST, cache_rate)


def patch(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
    *,
    cache_rate: int = -1,
) -> Path:
    """Add a PATCH route.

    Args:
        path_or_route: The path to this route, or the route itself.
        doc: The description of the route to be used in documentation.
        cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

    Example:
        ```py
        from view import patch

        @patch("/")
        async def index():
            return "Hello, view.py!"
        ```
    """
    return _method_wrapper(path_or_route, doc, Method.PATCH, cache_rate)


def put(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
    *,
    cache_rate: int = -1,
) -> Path:
    """Add a PUT route.

    Args:
        path_or_route: The path to this route, or the route itself.
        doc: The description of the route to be used in documentation.
        cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

    Example:
        ```py
        from view import put

        @put("/")
        async def index():
            return "Hello, view.py!"
        ```
    """
    return _method_wrapper(path_or_route, doc, Method.PUT, cache_rate)


def delete(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
    *,
    cache_rate: int = -1,
) -> Path:
    """Add a DELETE route.

    Args:
        path_or_route: The path to this route, or the route itself.
        doc: The description of the route to be used in documentation.
        cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

    Example:
        ```py
        from view import delete

        @delete("/")
        async def index():
            return "Hello, view.py!"
        ```
    """
    return _method_wrapper(path_or_route, doc, Method.DELETE, cache_rate)


def options(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
    *,
    cache_rate: int = -1,
) -> Path:
    """Add an OPTIONS route.

    Args:
        path_or_route: The path to this route, or the route itself.
        doc: The description of the route to be used in documentation.
        cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.

    Example:
        ```py
        from view import options

        @options("/")
        async def index():
            return "Hello, view.py!"
        ```
    """
    return _method_wrapper(path_or_route, doc, Method.OPTIONS, cache_rate)


_STR_METHOD_MAPPING: dict[StrMethod, Method] = {
    "GET": Method.GET,
    "POST": Method.POST,
    "PUT": Method.PUT,
    "PATCH": Method.PATCH,
    "DELETE": Method.DELETE,
    "OPTIONS": Method.OPTIONS,
}

def route(
    path_or_route: str | None | RouteOrCallable = None,
    doc: str | None = None,
    *,
    cache_rate: int = -1,
    methods: Iterable[StrMethod] | None = None
) -> Path:
    """Add a route that can be called with any method (or only specific methods).

    Args:
        path_or_route: The path to this route, or the route itself.
        doc: The description of the route to be used in documentation.
        cache_rate: Reload the cache for this route every x number of requests. `-1` means to never cache.
        methods: Methods that can be used to access this route. If this is `None`, then all methods are allowed.

    Example:
        ```py
        from view import route

        @route("/", methods=("GET", "POST"))
        async def index():
            return "Hello, view.py!"
        ```
    """
    return _method_wrapper(
        path_or_route,
        doc,
        None,
        cache_rate,
        method_list=[_STR_METHOD_MAPPING[i] for i in methods] if methods else None
    )



class _NoDefault:
    __VIEW_NODEFAULT__ = 1


_NoDefaultType = Type[_NoDefault]


def query(
    name: str,
    *tps: type[V],
    doc: str | None = None,
    default: V | None | _NoDefaultType = _NoDefault,
):
    """
    Add a route input for a query parameter.

    Args:
        name: The name of the parameter to read when the query string is received.
        tps: All the possible types that are allowed to be used. If none are specified, the type is `Any`.
        doc: Description of this parameter.
        default: The default value to use if the key was not received.

    Example:
        ```py
        from view import new_app, query

        app = new_app()

        @app.get("/")
        @query("greeting", str, doc="The greeting to use.", default="hello")
        def index(greeting: str):
            return f"{greeting}, world!"

        app.run()
        ```
    """

    frame = inspect.currentframe()
    assert frame, "currentframe() returned None"

    assert frame.f_back, "frame has no f_back"
    assert frame.f_back.f_back, "frame 2 has no f_back"

    target = frame.f_back.f_back

    for i in tps:
        with suppress(TypeError):
            setattr(i, "_view_scope", {**target.f_locals, **target.f_globals})

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
    """
    Add a route input for a body parameter.

    Args:
        name: The name of the parameter to read when the body is received.
        tps: All the possible types that are allowed to be used. If none are specified, the type is `Any`.
        doc: Description of this parameter.
        default: The default value to use if the key was not received.

    Example:
        ```py
        from view import new_app, body

        app = new_app()

        @app.get("/")
        @body("greeting", str, doc="The greeting to use.", default="hello")
        def index(greeting: str):
            return f"{greeting}, world!"

        app.run()
        ```
    """

    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.inputs.append(RouteInput(name, True, tps, default, doc, []))
        return route

    return inner


def context(r_or_none: RouteOrCallable | None = None):
    """Add a context input to the route."""
    def inner(r: RouteOrCallable) -> Route:
        route = _ensure_route(r)
        route.inputs.append(1)
        return route

    if r_or_none:
        return inner(r_or_none)

    return inner
