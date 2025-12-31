from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any, TypeAlias

from view.exceptions import InvalidTypeError, ViewError

__all__ = ("BodyMixin",)

BodyStream: TypeAlias = Callable[[], AsyncIterator[bytes]]


class BodyAlreadyUsedError(ViewError):
    """
    The body was already used on this response.

    Generally, this means that the same response object was executed multiple
    times.
    """

    def __init__(self) -> None:
        super().__init__("Body has already been consumed")


class InvalidJSONError(ViewError):
    """
    The body is not valid JSON data or something went wrong when parsing it.

    If this occurred when parsing the body for a request, the fix is
    usually to reraise this with an error 400 (Bad Request).
    """


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
            raise BodyAlreadyUsedError

        self.consumed = True

        buffer = BytesIO()
        async for data in self.receive_data():
            if __debug__ and not isinstance(data, bytes):
                raise InvalidTypeError(data, bytes)
            buffer.write(data)

        return buffer.getvalue()

    async def json(
        self, *, parse_function: Callable[[str], dict[str, Any]] = json.loads
    ) -> dict[str, Any]:
        """
        Read the body as JSON data.
        """

        data = await self.body()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise InvalidJSONError(
                "Body does not contain valid UTF-8 data"
            ) from error

        try:
            return parse_function(text)
        except Exception as error:
            raise InvalidJSONError("Failed to parse JSON") from error

    async def stream_body(self) -> AsyncIterator[bytes]:
        """
        Incrementally stream the body, not keeping the whole thing
        in-memory at a given time.
        """
        if self.consumed:
            raise BodyAlreadyUsedError

        self.consumed = True

        async for data in self.receive_data():
            if __debug__ and not isinstance(data, bytes):
                raise InvalidTypeError(data, bytes)
            yield data
