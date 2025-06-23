from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TYPE_CHECKING, TypeAlias

from multidict import CIMultiDict

from view.body import BodyMixin

if TYPE_CHECKING:
    from view.app import BaseApp

__all__ = "Method", "Request"

RequestHeaders: TypeAlias = CIMultiDict[str]
HeadersLike = RequestHeaders | dict[str, str] | dict[bytes, bytes]


def as_multidict(headers: HeadersLike | None, /) -> RequestHeaders:
    """
    Convenience function for casting a "header-like object" (or `None`)
    to a `CIMultiDict`.
    """
    if headers is None:
        return CIMultiDict()

    if isinstance(headers, CIMultiDict):
        return headers

    if not isinstance(headers, dict):
        raise TypeError(f"Invalid headers: {headers}")

    assert isinstance(headers, dict)
    multidict = CIMultiDict()
    for key, value in headers.items():
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        multidict[key] = value

    return multidict


class _UpperStrEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.upper()


class Method(_UpperStrEnum):
    """
    The HTTP request method.
    """

    GET = auto()
    POST = auto()
    PUT = auto()
    PATCH = auto()
    DELETE = auto()
    CONNECT = auto()
    OPTIONS = auto()
    TRACE = auto()
    HEAD = auto()


@dataclass(slots=True)
class Request(BodyMixin):
    """
    Dataclass representing an HTTP request.
    """

    app: "BaseApp"
    path: str
    method: Method
    headers: RequestHeaders
