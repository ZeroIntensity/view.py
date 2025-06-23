from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TYPE_CHECKING

from view.body import BodyMixin
from view.headers import RequestHeaders

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
