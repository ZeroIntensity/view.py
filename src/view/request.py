from dataclasses import dataclass, field
from enum import StrEnum, auto
from io import BytesIO
from typing import AsyncGenerator, AsyncIterator, Callable, TypeAlias

from multidict import CIMultiDict

from view.app import BaseApp

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


BodyStream: TypeAlias = Callable[[], AsyncIterator[bytes]]


@dataclass(slots=True)
class Request:
    """
    Dataclass representing an HTTP request.
    """

    app: BaseApp
    path: str
    method: Method
    headers: CIMultiDict
    receive_data: BodyStream | None = None
    consumed: bool = field(init=False, default=False)

    async def body(self) -> bytes:
        if self.consumed:
            raise RuntimeError("body has already been consumed")

        self.consumed = True
        if self.receive_data is None:
            return b""

        buffer = BytesIO()
        async for data in self.receive_data():
            buffer.write(data)

        return buffer.getvalue()

    async def stream_body(self) -> AsyncGenerator[bytes]:
        if self.consumed:
            raise RuntimeError("body has already been consumed")

        self.consumed = True
        if self.receive_data is None:
            yield b""
            return

        async for data in self.receive_data():
            yield data
