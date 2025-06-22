from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TYPE_CHECKING

from multidict import CIMultiDict

from view.body import BodyMixin

if TYPE_CHECKING:
    from view.app import BaseApp

__all__ = "Method", "Request"


class Method(StrEnum):
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
    headers: CIMultiDict
