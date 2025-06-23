from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from typing import AsyncGenerator, AsyncIterator, Callable, TypeAlias

__all__ = ("BodyMixin",)

BodyStream: TypeAlias = Callable[[], AsyncIterator[bytes]]


@dataclass(slots=True)
class BodyMixin:
    """
    Mixin dataclass for common HTTP body operations.
    """
    receive_data: BodyStream
    consumed: bool = field(init=False, default=False)

    async def body(self) -> bytes:
        """
        Read the full body from the stream.
        """
        if self.consumed:
            raise RuntimeError("body has already been consumed")

        self.consumed = True

        buffer = BytesIO()
        async for data in self.receive_data():
            buffer.write(data)

        return buffer.getvalue()

    async def stream_body(self) -> AsyncGenerator[bytes]:
        """
        Incrementally stream the body, not keeping the whole thing
        in-memory at a given time.
        """
        if self.consumed:
            raise RuntimeError("body has already been consumed")

        self.consumed = True

        async for data in self.receive_data():
            yield data
