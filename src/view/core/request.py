from __future__ import annotations

import sys
import urllib.parse
from dataclasses import dataclass, field
from enum import auto
from typing import TYPE_CHECKING, Any

from view.core.body import BodyMixin
from view.core.router import normalize_route
from view.core.multi_map import MultiMap

if TYPE_CHECKING:
    from collections.abc import Mapping

    from view.core.app import BaseApp
    from view.core.headers import HTTPHeaders

__all__ = "Method", "Request"

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class _UpperStrEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(
        name: str,
        *_: Any,
    ) -> str:
        return name.upper()


class Method(_UpperStrEnum):
    """
    The HTTP request method.
    """

    GET = auto()
    """
    The GET method requests a representation of the specified resource.

    Requests using GET should only retrieve data and should not contain
    a request content.
    """

    POST = auto()
    """
    The POST method submits an entity to the specified resource, often causing
    a change in state or side effects on the server.
    """

    PUT = auto()
    """
    The PUT method replaces all current representations of the target resource
    with the request content.
    """

    PATCH = auto()
    """
    The PATCH method applies partial modifications to a resource.
    """

    DELETE = auto()
    """
    The DELETE method deletes the specified resource.
    """

    CONNECT = auto()
    """
    The CONNECT method establishes a tunnel to the server identified by the
    target resource.
    """

    OPTIONS = auto()
    """
    The OPTIONS method describes the communication options for the target
    resource.
    """

    TRACE = auto()
    """
    The TRACE method performs a message loop-back test along the path to the
    target resource.
    """

    HEAD = auto()
    """
    The HEAD method asks for a response identical to a GET request, but
    without a response body.
    """


@dataclass(slots=True)
class Request(BodyMixin):
    """
    Dataclass representing an HTTP request.
    """

    app: BaseApp
    """
    The app associated with the HTTP request.
    """

    path: str
    """
    The path of the request, with the leading '/' and without a trailing '/'
    or query string.
    """

    method: Method
    """
    The HTTP method of the request. See `Method`.
    """

    headers: HTTPHeaders
    """
    A "multi-dictionary" containing the request headers. This is `dict`-like,
    but if a header has multiple values, it is represented by a list.
    """

    query_parameters: MultiMap[str, str]
    """
    The query string parameters of the HTTP request.
    """

    path_parameters: Mapping[str, str] = field(
        default_factory=dict, init=False
    )
    """
    The path parameters of this request.
    """

    def __post_init__(self) -> None:
        self.path = normalize_route(self.path)


def extract_query_parameters(query_string: str | bytes) -> MultiMap[str, str]:
    """
    Extract a query string from a URL and return it as a multi-map.
    """
    if isinstance(query_string, bytes):
        query_string = query_string.decode("utf-8")

    assert isinstance(query_string, str), query_string
    return MultiMap(urllib.parse.parse_qsl(query_string))
