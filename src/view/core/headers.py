from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeAlias

from typing_extensions import Self

from view.core.multi_map import MultiMap
from view.exceptions import InvalidTypeError

if TYPE_CHECKING:
    from view.run.asgi import ASGIHeaders
    from view.run.wsgi import WSGIHeaders

__all__ = (
    "HTTPHeaders",
    "HeadersLike",
    "as_real_headers",
    "asgi_to_headers",
    "headers_to_asgi",
    "wsgi_to_headers",
)


class LowerStr(str):
    """
    A string that always acts in lowercase. This is useful for case-insensitive
    comparisons.
    """

    __slots__ = ()

    def __new__(cls, data: object) -> Self:
        return super().__new__(cls, cls._to_lower(data))

    @staticmethod
    def _to_lower(data: object) -> object:
        if isinstance(data, str):
            data = data.lower()

        return data

    def __contains__(self, key: str, /) -> bool:
        return super().__contains__(key.lower())

    def __eq__(self, string: object) -> bool:
        return super().__eq__(self._to_lower(string))

    def __ne__(self, value: object, /) -> bool:
        return super().__ne__(self._to_lower(value))

    def __hash__(self) -> int:
        return hash(str(self))


class HTTPHeaders(MultiMap[str, str]):
    """
    Case-insensitive multi-map of HTTP headers.
    """

    def __getitem__(self, key: str, /) -> str:
        return super().__getitem__(LowerStr(key))

    def __contains__(self, key: object, /) -> bool:
        return super().__contains__(LowerStr(key))

    def __repr__(self) -> str:
        return f"HTTPHeaders({self.as_sequence()})"

    def get_exactly_one(self, key: str) -> str:
        return super().get_exactly_one(LowerStr(key))

    def with_new_value(self, key: str, value: str) -> HTTPHeaders:
        new_sequence = [*list(self.as_sequence()), (LowerStr(key), value)]
        return type(self)(new_sequence)


HeadersLike: TypeAlias = (
    HTTPHeaders | Mapping[str, str] | Mapping[bytes, bytes]
)


def as_real_headers(headers: HeadersLike | None, /) -> HTTPHeaders:
    """
    Convenience function for casting a "header-like object" (or `None`)
    to a `MultiMap`.
    """
    if headers is None:
        return HTTPHeaders()

    if isinstance(headers, HTTPHeaders):
        return headers

    if __debug__ and not isinstance(headers, Mapping):
        raise InvalidTypeError(Mapping, headers)

    assert isinstance(headers, dict)
    all_values: list[tuple[LowerStr, str]] = []

    for key, value in headers.items():
        if isinstance(key, bytes):
            key = key.decode("utf-8")  # noqa: PLW2901

        if isinstance(value, bytes):
            value = value.decode("utf-8")  # noqa: PLW2901

        all_values.append((LowerStr(key), value))

    return HTTPHeaders(all_values)


def wsgi_to_headers(environ: Mapping[str, Any]) -> HTTPHeaders:
    """
    Convert WSGI headers (from the `environ`) to a case-insensitive multi-map.
    """
    values: list[tuple[LowerStr, str]] = []

    for key, value in environ.items():
        if not key.startswith("HTTP_"):
            continue

        assert isinstance(value, str)
        key = key.removeprefix("HTTP_").replace("_", "-").lower()  # noqa: PLW2901
        values.append((LowerStr(key), value))

    return HTTPHeaders(values)


def headers_to_wsgi(headers: HTTPHeaders) -> WSGIHeaders:
    """
    Convert a case-insensitive multi-map to a WSGI header iterable.
    """

    wsgi_headers: WSGIHeaders = []
    for key, value in headers.items():
        wsgi_headers.append((str(key), value))

    return wsgi_headers


def asgi_to_headers(headers: ASGIHeaders, /) -> HTTPHeaders:
    """
    Convert ASGI headers to a case-insensitive multi-map.
    """
    values: list[tuple[LowerStr, str]] = []

    for key, value in headers:
        lower_str = LowerStr(key.decode("utf-8"))
        values.append((lower_str, value.decode("utf-8")))

    return MultiMap(values)


def headers_to_asgi(headers: HTTPHeaders, /) -> ASGIHeaders:
    """
    Convert a case-insensitive multi-map to an ASGI header iterable.
    """
    asgi_headers: ASGIHeaders = []

    for key, value in headers:
        asgi_headers.append((key.encode("utf-8"), value.encode("utf-8")))

    return asgi_headers
