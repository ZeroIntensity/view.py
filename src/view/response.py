from __future__ import annotations

from datetime import datetime as DateTime
from pathlib import Path
from typing import Any, Dict, Generic, TextIO, TypeVar, Union

import ujson

from .components import DOMNode
from .exceptions import InvalidResultError
from .typing import BodyTranslateStrategy, SameSite, ViewResult
from .util import timestamp

T = TypeVar("T")

__all__ = "Response", "HTML", "JSON", "to_response"

_Find = None
HTMLContent = Union[TextIO, str, Path, DOMNode]


class Response(Generic[T]):
    """Wrapper for responses."""

    def __init__(
        self,
        body: T,
        status: int = 200,
        headers: dict[str, str] | None = None,
        *,
        body_translate: BodyTranslateStrategy | None = _Find,
    ) -> None:
        self.body = body
        self.status = status
        self.headers = headers or {}
        self._raw_headers: list[tuple[bytes, bytes]] = []

        if body_translate:
            self.translate = body_translate
        else:
            self.translate = (
                "str" if not hasattr(body, "__view_result__") else "result"
            )

    def _custom(self, body: T) -> str:
        raise NotImplementedError(
            'the "custom" translate strategy can only be used in subclasses that implement it'
        )  # noqa

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
        """Set a cookie.

        Args:
            key: Cookie name.
            value: Cookie value.
            max_age: Max age of the cookies.
            expires: When the cookie expires.
            domain: Domain the cookie is valid at.
            http_only: Whether the cookie should be HTTP only.
            same_site: SameSite setting for the cookie.
            partitioned: Whether to tie it to the top level site.
            secure: Whether the cookie should enforce HTTPS."""
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
        headers: list[tuple[bytes, bytes]] = [*self._raw_headers]

        for k, v in self.headers.items():
            headers.append((k.encode(), v.encode()))

        return tuple(headers)

    def __view_result__(self) -> ViewResult:
        body: str = ""
        if self.translate == "str":
            body = str(self.body)
        elif self.translate == "repr":
            body = repr(self.body)
        elif self.translate == "custom":
            body = self._custom(self.body)
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
    """HTML response wrapper."""

    def __init__(
        self,
        body: HTMLContent,
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(body, status, headers, body_translate="custom")
        self._raw_headers.append((b"content-type", b"text/html"))

    def _custom(self, body: HTMLContent) -> str:
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


class JSON(Response[Dict[str, Any]]):
    """JSON response wrapper."""

    def __init__(
        self,
        body: dict[str, Any],
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(body, status, headers, body_translate="custom")
        self._raw_headers.append((b"content-type", b"application/json"))

    def _custom(self, body: dict[str, Any]) -> str:
        return ujson.dumps(body)


def to_response(result: ViewResult) -> Response[str]:
    """Cast a result from a route function to a `Response` object."""

    if hasattr(result, "__view_result__"):
        result = result.__view_result__()  # type: ignore
        return to_response(result)

    if isinstance(result, tuple):
        status: int = 200
        headers: dict[str, str] = {}
        raw_headers: list[tuple[bytes, bytes]] = []
        body: str | None = None

        for value in result:
            if isinstance(value, int):
                status = value
            elif isinstance(value, str):
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

    assert isinstance(result, str)
    return Response(result)
