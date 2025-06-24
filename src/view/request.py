from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import TYPE_CHECKING

from view.body import BodyMixin
from view.headers import RequestHeaders
from view.router import normalize_route

if TYPE_CHECKING:
    from view.app import BaseApp

__all__ = "Method", "Request"


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

    app: "BaseApp"
    path: str
    method: Method
    headers: RequestHeaders
    parameters: dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.path = normalize_route(self.path)
