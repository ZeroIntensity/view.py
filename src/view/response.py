"""
view.py public response APIs

This module contains the `Response` class, which is conventionally used as the base response in view.py
All other classes that inherit from it are contained in this module.
"""
from __future__ import annotations

import uuid
from contextlib import suppress
from datetime import datetime as DateTime
from pathlib import Path
from typing import Any, Dict, Generic, TextIO, TypeVar, Union

import aiofiles
import ujson
from typing_extensions import final

from .components import DOMNode
from .exceptions import InvalidResultError
from .typing import BodyTranslateStrategy, ResponseBody, SameSite, ViewResult
from .util import timestamp

T = TypeVar("T")

__all__ = "Response", "HTML", "JSON", "to_response"

_Find = None
HTMLContent = Union[TextIO, str, Path, DOMNode]


class Response(Generic[T]):
    """
    Base view.py response class.
    
    Technically speaking, it's not required for an object to inherit from this class if it wants to be used as a response object - to do that, all an object has to do is implement `__view_result__`.
    However, it's good convention to use this as the base class for objects that are solely used as a response.

    It's probably not a good idea to reuse responses (i.e. return the same `Response` object from multiple calls), but it's not prevented.
    """

    def __init__(
        self,
        body: T,
        status: int = 200,
        headers: dict[str, str] | None = None,
        *,
        body_translate: BodyTranslateStrategy | None = _Find,
        content_type: str = "text/plain"
    ) -> None:
        """
        Args:
            body: Response body. This can be any type, and the `body_translate` parameter determines how it's converted into a string that view.py can read.
            status: Status code to send to the user.
            headers: Dictionary containing the response headers.
            body_translate: This determines how the underlying `__view_result__` translates the body object into a string. By default, if the body object has a `__view_result__` attribute, this is set to `"result"`, and `"str"` otherwise. If this is `"custom"`, the `translate_body` method is called which can define any logic to translate the object. Note that if you're directly instantiating `Response`, you probably don't want to set this parameter - it's more for use from subclasses.
            content_type: MIME type of the body. `"text/plain"` by default.
        """
        self.body = body
        """Implementation-specific body object. This will always be what's passed to the constructor of `Response`"""
        self.status = status
        """Status code to be sent alongside the response."""
        self.headers = headers or {}
        """Headers to be sent along with the response."""
        self.content_type: str = content_type
        """MIME type of the body. This is added to the headers last-minute in the `__view_result__` call, so you can update this value after it has been set."""
        self._raw_headers: list[tuple[bytes, bytes]] = []

        if body_translate:
            self.translate = body_translate
        else:
            self.translate = "str" if not hasattr(body, "__view_result__") else "result"

    def translate_body(self, body: T) -> str | bytes:
        """
        Translate the body via the `"custom"` body translate strategy. On classes that don't implement this, a `NotImplementedError` is raised.

        Args:
            body: Body object to translate to a string. This is dependent on the class.

        Returns:
            A `str` or `bytes` containing the translated body.
        """
        raise NotImplementedError(
            'the "custom" translate strategy can only be used in subclasses that implement it'
        )  # noqa

    @final
    def cookie(
        self,
        key: str,
        value: str = "",
        *,
        max_age: int | None = None,
        expires: int | DateTime | None = None,
        path: str | None = None,
        domain: str | None = None,
        http_only: bool = False,
        same_site: SameSite = "lax",
        partitioned: bool = False,
        secure: bool = False,
    ) -> None:
        """
        Set a cookie.

        Args:
            key: Cookie name.
            value: Cookie value.
            max_age: Max age of the cookies.
            expires: When the cookie expires.
            domain: Domain the cookie is valid at.
            http_only: Whether the cookie should be HTTP only.
            same_site: SameSite setting for the cookie.
            partitioned: Whether to tie it to the top level site.
            secure: Whether the cookie should enforce HTTPS.
        """
        cookie_str = f"{key}={value}; SameSite={same_site}".encode()

        if expires:
            dt = (
                expires
                if isinstance(expires, DateTime)
                else DateTime.fromtimestamp(expires)
            )
            ts = timestamp(dt)
            cookie_str += f"; Expires={ts}".encode()

        if http_only:
            cookie_str += b"; HttpOnly"

        if domain:
            cookie_str += f"; Domain={domain}".encode()

        if max_age:
            cookie_str += f"; Max-Age={max_age}".encode()

        if partitioned:
            cookie_str += b"; Partitioned"

        if secure:
            cookie_str += b"; Secure"

        if path:
            cookie_str += f"; Path={path}".encode()

        self._raw_headers.append((b"Set-Cookie", cookie_str))

    def _build_headers(self) -> tuple[tuple[bytes, bytes], ...]:
        headers: list[tuple[bytes, bytes]] = [*self._raw_headers, (b"content-type", self.content_type.encode())]

        for k, v in self.headers.items():
            headers.append((k.encode(), v.encode()))

        return tuple(headers)

    @final
    def __view_result__(self) -> ViewResult:
        """view.py response function. This should not be called manually, and it's implementation should be considered unstable, but this will always be here."""
        body: str | bytes = ""
        if self.translate == "str":
            if isinstance(self.body, bytes):
                body = self.body.decode()
            else:
                body = str(self.body)
        elif self.translate == "repr":
            body = repr(self.body)
        elif self.translate == "custom":
            body = self.translate_body(self.body)
        else:
            view_result = getattr(self.body, "__view_result__", None)

            if not view_result:
                raise AttributeError(f"{self.body!r} has no __view_result__")

            body_res = view_result()
            if isinstance(body_res, str):
                body = body_res
            else:
                for i in body_res:
                    if isinstance(i, str):
                        body = i

        return body, self.status, self._build_headers()


class HTML(Response[HTMLContent]):
    """
    HTML response wrapper.
    """

    def __init__(
        self,
        body: HTMLContent,
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(body, status, headers, body_translate="custom", content_type="text/html")

    def translate_body(self, body: HTMLContent) -> str:
        parsed_body = ""

        if isinstance(body, Path):
            parsed_body = body.read_text()
        elif isinstance(body, str):
            parsed_body = body
        elif isinstance(body, DOMNode):
            parsed_body = body.data
        else:
            try:
                parsed_body = body.read()
            except AttributeError:
                raise TypeError(
                    f"expected TextIO, str, Path, or DOMNode, not {type(body)}",  # noqa
                ) from None

        return parsed_body

    @classmethod
    async def from_file(cls, path: str | Path) -> HTML:
        """
        Read an HTML file and load it as a response.
        Roughly speaking, this shouldn't be used over `template()`, but it's a better option if you have a pure HTML file that doesn't need to get put through an extra template step.

        Args:
            path: `str` or `Path` object containing the path to the HTML file.

        Example:
            ```py
            from view import HTML, get

            @get("/")
            async def index():
                return await HTML.from_file("content/index.html")
            ```
        """
        async with aiofiles.open(path) as f:
            return cls(await f.read())


class JSON(Response[Dict[str, Any]]):
    """
    JSON response wrapper.

    Dictionaries passed to this object are serialized by `ujson.dumps`.
    """

    def __init__(
        self,
        body: dict[str, Any],
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(body, status, headers, body_translate="custom", content_type="application/json",)

    def translate_body(self, body: dict[str, Any]) -> str:
        return ujson.dumps(body)


def to_response(result: ViewResult) -> Response[ResponseBody]:
    """Cast a result from a route function to a `Response` object."""

    if hasattr(result, "__view_result__"):
        result = result.__view_result__()  # type: ignore
        return to_response(result)

    if isinstance(result, tuple):
        status: int = 200
        headers: dict[str, str] = {}
        raw_headers: list[tuple[bytes, bytes]] = []
        body: ResponseBody | None = None

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


async def _reactpy_bootstrap(self: Component) -> ViewResult:
    from .app import get_app

    react_id = uuid.uuid4().hex
    app = get_app()
    app.reactive_sessions[react_id] = self
    return await app.template("./client/dist/index.html", engine="view")

with suppress(ImportError):
    from reactpy.core.component import Component

    Component.__view_result__ = _reactpy_bootstrap  # type: ignore
