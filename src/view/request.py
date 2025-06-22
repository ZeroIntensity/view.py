from dataclasses import dataclass
from enum import StrEnum, auto

from multidict import CIMultiDict

from view.app import BaseApp
from view.body import BodyMixin

__all__ = "Method", "Request"


class Method(StrEnum):
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

    app: BaseApp
    path: str
    method: Method
    headers: CIMultiDict
