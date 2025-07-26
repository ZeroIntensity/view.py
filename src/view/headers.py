from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeAlias

from multidict import CIMultiDict

from view.exceptions import InvalidType

if TYPE_CHECKING:
    from view.asgi import ASGIHeaders

__all__ = (
    "RequestHeaders",
    "HeadersLike",
    "as_multidict",
    "asgi_as_multidict",
    "multidict_as_asgi",
    "wsgi_as_multidict",
)

RequestHeaders: TypeAlias = CIMultiDict[str]
HeadersLike = RequestHeaders | dict[str, str] | dict[bytes, bytes]


def as_multidict(headers: HeadersLike | None, /) -> RequestHeaders:
    """
    Convenience function for casting a "header-like object" (or `None`)
    to a `CIMultiDict`.
    """
    if headers is None:
        return CIMultiDict[str]()

    if isinstance(headers, CIMultiDict):
        return headers

    if __debug__ and not isinstance(headers, dict):
        raise InvalidType(dict, headers)

    assert isinstance(headers, dict)
    multidict = CIMultiDict[str]()
    for key, value in headers.items():
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        multidict[key] = value

    return multidict


def wsgi_as_multidict(environ: dict[str, Any]) -> RequestHeaders:
    """
    Convert WSGI headers (from the `environ`) to a case-insensitive multidict.
    """
    headers = CIMultiDict[str]()

    for key, value in environ.items():
        if not key.startswith("HTTP_"):
            continue

        assert isinstance(value, str)
        key = key.lstrip("HTTP_")
        headers[key.replace("_", "-").lower()] = value

    return headers


def asgi_as_multidict(headers: ASGIHeaders, /) -> RequestHeaders:
    """
    Convert ASGI headers to a case-insensitive multidict.
    """
    multidict = CIMultiDict[str]()

    for key, value in headers:
        multidict[key.decode("utf-8")] = value.decode("utf-8")

    return multidict


def multidict_as_asgi(headers: RequestHeaders, /) -> ASGIHeaders:
    """
    Convert a case-insensitive multidict to an ASGI header iterable.
    """
    asgi_headers: ASGIHeaders = []

    for key, value in headers:
        asgi_headers.append((key.encode("utf-8"), value.encode("utf-8")))

    return asgi_headers
