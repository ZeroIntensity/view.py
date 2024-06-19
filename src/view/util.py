"""
view.py public utility APIs

This module contains general utility functions.
Most of these exist because they are used somewhere else in view.py, it's just nice to provide the functionality publicly.

For example, `timestamp()` is used by `cookie()` in `Response`, but it could be useful to generate timestamps for other cases.
"""
from __future__ import annotations

import json
import logging
import os
from collections.abc import Awaitable
from datetime import datetime as DateTime
from email.utils import formatdate
from typing import TYPE_CHECKING, Callable, TypeVar, Union, overload

from typing_extensions import ParamSpec, deprecated

from _view import Context, dummy_context

from ._logging import Internal, Service
from ._util import run_path, shell_hint
from .exceptions import (AppNotFoundError, BadEnvironmentError,
                         InvalidResultError)
from .typing import (ErrorStatusCode, StrResponseBody, SupportsViewResult,
                     ViewResult)

if TYPE_CHECKING:
    from .app import App
    from .response import Response

__all__ = ("run", "env", "enable_debug", "timestamp", "extract_path", "expect_errors", "call_result", "to_response")

T = TypeVar("T")
P = ParamSpec("P")


def extract_path(path: str) -> App:
    """
    Extract an `App` instance from a path.

    Args:
        path: Path to the file and the app name in the format of `/path/to/app.py:app_name`.

    Raises:
        AppNotFoundError: File path does not exist.
        AttributeError: File was found and loaded, but is missing the attribute name specified by `path`.
        TypeError: The object found is not a `view.App` object.

    Example:
        ```py
        from view import extract_path

        app = extract_path("app.py:app")
        app.run()
        ```
    """
    from .app import App

    split = path.split(":", maxsplit=1)

    if len(split) != 2:
        raise ValueError(
            "module string should be in the format of `/path/to/app.py:app_name`",
        )

    file_path = os.path.abspath(split[0])

    try:
        mod = run_path(file_path)
    except FileNotFoundError as e:
        raise AppNotFoundError(f'"{split[0]}" in {path} does not exist') from e

    try:
        target = mod[split[1]]
    except KeyError:
        raise AttributeError(f'"{split[1]}" in {path} does not exist') from None

    if not isinstance(target, App):
        raise TypeError(f"{target!r} is not an instance of view.App")

    return target


@deprecated(
    "Use run() on `App` instead. If you have an app path, use `extract_path()`, followed by run()"
)
def run(app_or_path: str | App) -> None:
    """
    Run a view app.

    Args:
        app_or_path: App object or path to run.
    """
    from .app import App

    if isinstance(app_or_path, App):
        app_or_path.run()
        return

    target = extract_path(app_or_path)
    target._run()


def enable_debug():
    """
    Enable debug mode. The exact details of what this does should be considered unstable.

    Generally, this will enable debug logging.
    """
    internal = Internal.log
    internal.disabled = False
    internal.setLevel(logging.DEBUG)
    internal.addHandler(
        logging.StreamHandler(open("view_internal.log", "w", encoding="utf-8"))
    )
    Service.log.addHandler(
        logging.StreamHandler(open("view_service.log", "w", encoding="utf-8"))
    )

    Internal.info("debug mode enabled")
    os.environ["VIEW_DEBUG"] = "1"


EnvConv = Union[str, int, bool, dict]

# good god why does mypy suck at the very thing it's designed to do


@overload
def env(key: str, *, tp: type[str] = str) -> str:  # type: ignore
    ...


@overload
def env(key: str, *, tp: type[int] = int) -> int:  # type: ignore
    ...


@overload
def env(key: str, *, tp: type[bool] = bool) -> bool:  # type: ignore
    ...


@overload
def env(key: str, *, tp: type[dict] = dict) -> dict:  # type: ignore
    ...


def env(key: str, *, tp: type[EnvConv] = str) -> EnvConv:
    """
    Get and parse an environment variable.

    Args:
        key: Environment variable to access.
        tp: Type to convert to.

    Example:
        ```py
        from view import new_app, env

        app = new_app()

        @app.get("/")
        def index():
            return env("FOO")

        app.run()
        ```

    Raises:
        BadEnvironmentError: Environment variable is not set or does not match the type.
        TypeError: `tp` parameter is not a valid type.
    """
    value = os.environ.get(key)

    if not value:
        raise BadEnvironmentError(
            f'environment variable "{key}" not set',
            hint=shell_hint(
                f"set {key}=..." if os.name == "nt" else f"export {key}=..."
            ),
        )

    if tp is str:
        return value

    if tp is int:
        try:
            return int(value)
        except ValueError:
            raise BadEnvironmentError(
                f"{value!r} (key {key!r}) is not int-like"
            ) from None

    if tp is dict:
        try:
            return json.loads(value)
        except ValueError:
            raise BadEnvironmentError(f"{value!r} ({key!r}) is not dict-like")

    if tp is bool:
        value = value.lower()
        if value not in {"true", "false"}:
            raise BadEnvironmentError(f"{value!r} ({key!r}) is not bool-like")

        return value == "true"

    raise TypeError(f"invalid type in env(): {tp}")


_Now = None


def timestamp(tm: DateTime | None = _Now) -> str:
    """
    RFC 1123 Compliant Timestamp. This is used by `Response` internally.

    Args:
        tm: Date object to create a timestamp for. Now by default.
    """
    stamp: float = DateTime.now().timestamp() if not tm else tm.timestamp()
    return formatdate(stamp, usegmt=True)


_UseErrMessage = None


def expect_errors(
    *errs: BaseException,
    message: str | None = _UseErrMessage,
    status: ErrorStatusCode = 400,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Raise an HTTP error if any of `errs` occurs during execution.
    This function is a decorator.

    Args:
        errs: All errors to recognize.
        message: Message to pass to `HTTPError`. Uses the message with the raised exception if `None`.
        status: Status code to return. `400` by default.

    Example:
        ```py
        from view import get, expect_errors, context, Context

        @get("/")
        @context
        @expect_errors(KeyError, message="Missing header.")
        def index(ctx: Context):
            my_header = ctx.headers["www-token"]
            return ...
        ```
    """

    def inner(func: Callable[P, T]) -> Callable[P, T]:
        def deco(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except BaseException as e:
                if e not in errs:
                    raise

                from .app import HTTPError
                raise HTTPError(message=message or str(e), status=status)

        return deco

    return inner

async def call_result(result: SupportsViewResult, *, ctx: Context | None = None) -> ViewResult:
    """
    Call the `__view_result__` on an object.

    Args:
        result: An object containing a `__view_result__` method.
        ctx: The `Context` object to pass. If this is `None`, then a dummy context with incorrect values is generated. Only pass `None` here when you're sure that the `__view_result__` does not need the context.
    """
    from .app import get_app
    app: App | None = None

    try:
        app = get_app()
    except BadEnvironmentError:
        app = None

    ctx = ctx or dummy_context(app)
    coro_or_res = result.__view_result__(ctx)
    if isinstance(coro_or_res, Awaitable):
        return await coro_or_res

    return coro_or_res


async def to_response(result: ViewResult | Awaitable[ViewResult], *, ctx: Context | None = None,) -> Response[StrResponseBody]:
    """
    Cast a result from a route function to a `Response` object.

    Args:
        result: Result to cast. This can be any valid view.py response, such as a string, a tuple, or some object that implements `__view_result__`.
        ctx: `Context` object to pass to `call_result`, if the `result` parameter supports `__view_result__`.

    Example:
        ```py
        from view import new_app, to_response

        app = new_app()

        @app.get("/")
        def index():
            return "Hello, world!"

        @app.get("/test")
        async def test():
            response = await to_response(index())
            assert response.body == "Hello, world!"
            return ...

        app.run()
        ```
    """
    from .response import Response

    if isinstance(result, Awaitable):
        result = await result

    if isinstance(result, SupportsViewResult):
        res = await call_result(result, ctx=ctx)
        return await to_response(res)

    if isinstance(result, tuple):
        status: int = 200
        headers: dict[str, str] = {}
        raw_headers: list[tuple[bytes, bytes]] = []
        body: StrResponseBody | None = None

        for value in result:
            if isinstance(value, int):
                status = value
            elif isinstance(value, (str, bytes)):
                body = value
            elif isinstance(value, dict):
                headers = value
            elif isinstance(value, list):
                raw_headers = value
            else:
                raise InvalidResultError(
                    f"{value!r} is not a valid response tuple item"
                )

        if not body:
            raise InvalidResultError("result has no body")

        res = Response(body, status, headers)
        res._raw_headers = raw_headers
        return res

    assert isinstance(result, (str, bytes))
    return Response(result)
