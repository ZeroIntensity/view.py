from __future__ import annotations

from datetime import datetime as DateTime
from pathlib import Path
from typing import Generic, TextIO, TypeVar

from .components import DOMNode
from .typing import BodyTranslateStrategy, SameSite
from .util import timestamp

T = TypeVar("T")

__all__ = "Response", "HTML"

_Find = None


class Response(Generic[T]):
    def __init__(
        self,
        body: T | None = None,
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

    def __view_result__(self):
        body: str = ""
        if self.translate == "str":
            body = str(self.body)
        elif self.translate == "repr":
            body = repr(self.body)
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


class HTML(Response[str]):
    def __init__(
        self,
        body: TextIO | str | Path | DOMNode,
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
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

        super().__init__(parsed_body, status, headers)
        self._raw_headers.append((b"content-type", b"text/html"))
