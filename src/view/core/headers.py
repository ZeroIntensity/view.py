from __future__ import annotations

from collections.abc import Mapping
from collections import UserString
from typing import TYPE_CHECKING, Any, TypeAlias

from view.exceptions import InvalidTypeError
from view.core.multi_map import MultiMap

if TYPE_CHECKING:
    from view.run.asgi import ASGIHeaders

__all__ = (
    "RequestHeaders",
    "HeadersLike",
    "as_real_headers",
    "asgi_to_headers",
    "headers_to_asgi",
    "wsgi_to_headers",
)


class LowerStr(UserString):
    """
    A string that always acts in lowercase. This is useful for case-insensitive
    comparisons.
    """

    def __init__(self, data: object) -> None:
        super().__init__(self._to_lower(data))

    def _to_lower(self, data: object) -> object:
        if isinstance(data, str):
            data = data.lower()

        return data

    def __contains__(self, char: object) -> bool:
        return super().__contains__(self._to_lower(char))

    def __eq__(self, string: object) -> bool:
        return super().__eq__(self._to_lower(string))

    def __ne__(self, value: object, /) -> bool:
        return super().__ne__(self._to_lower(value))

    def __hash__(self) -> int:
        return hash(self.data)


RequestHeaders: TypeAlias = MultiMap[LowerStr, str]
HeadersLike: TypeAlias = (
    RequestHeaders | Mapping[str, str] | Mapping[bytes, bytes]
)


def as_real_headers(headers: HeadersLike | None, /) -> RequestHeaders:
    """
    Convenience function for casting a "header-like object" (or `None`)
    to a `MultiMap`.
    """
    if headers is None:
        return MultiMap[LowerStr, str]()

    if isinstance(headers, MultiMap):
        return headers

    if __debug__ and not isinstance(headers, Mapping):
        raise InvalidTypeError(Mapping, headers)

    assert isinstance(headers, dict)
    all_values: list[tuple[LowerStr, str]] = []

    for key, value in headers.items():
        if isinstance(key, bytes):
            key = key.decode("utf-8")  # noqa

        if isinstance(value, bytes):
            value = value.decode("utf-8")  # noqa

        all_values.append((LowerStr(key), value))

    return MultiMap(all_values)


def wsgi_to_headers(environ: Mapping[str, Any]) -> RequestHeaders:
    """
    Convert WSGI headers (from the `environ`) to a case-insensitive multi-map.
    """
    values: list[tuple[LowerStr, str]] = []

    for key, value in environ.items():
        if not key.startswith("HTTP_"):
            continue

        assert isinstance(value, str)
        key = key.removeprefix("HTTP_").replace("_", "-").lower()  # noqa
        values.append((LowerStr(key), value))

    return MultiMap(values)


def asgi_to_headers(headers: ASGIHeaders, /) -> RequestHeaders:
    """
    Convert ASGI headers to a case-insensitive multi-map.
    """
    values: list[tuple[LowerStr, str]] = []

    for key, value in headers:
        lower_str = LowerStr(key.decode("utf-8"))
        values.append((lower_str, value.decode("utf-8")))

    return MultiMap(values)


def headers_to_asgi(headers: RequestHeaders, /) -> ASGIHeaders:
    """
    Convert a case-insensitive multi-map to an ASGI header iterable.
    """
    asgi_headers: ASGIHeaders = []

    for key, value in headers:
        asgi_headers.append((key.encode("utf-8"), value.encode("utf-8")))

    return asgi_headers
