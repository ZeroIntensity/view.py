from __future__ import annotations

from dataclasses import dataclass
from typing import AnyStr, AsyncGenerator, TypeAlias

from loguru import logger
from multidict import CIMultiDict

from view.body import BodyMixin

__all__ = "Response", "ResponseLike"


@dataclass(slots=True)
class Response(BodyMixin):
    """
    High-level dataclass representing a response from a view.
    """

    status_code: int
    headers: CIMultiDict

    async def as_tuple(self) -> tuple[bytes, int, CIMultiDict]:
        """
        Process the response as a tuple. This is mainly useful
        for assertions in testing.
        """
        return (await self.body(), self.status_code, self.headers)


@dataclass(slots=True)
class BytesResponse(Response):
    """
    Simple in-memory response for a byte string.
    """

    content: bytes

    def as_tuple_sync(self) -> tuple[bytes, int, CIMultiDict]:
        return (self.content, self.status_code, self.headers)

    @classmethod
    def from_bytes(
        cls, content: bytes, status_code: int, headers: CIMultiDict
    ) -> BytesResponse:
        async def stream() -> AsyncGenerator[bytes]:
            yield content

        return cls(stream, status_code, headers, content)


ResponseLike: TypeAlias = Response | AnyStr


def wrap_response(response: ResponseLike) -> Response:
    """
    Wrap a response from a view into a `Response` object.
    """
    logger.debug(f"Got response: {response}")
    if isinstance(response, Response):
        return response

    content: bytes
    if isinstance(response, str):
        content = response.encode()
    elif isinstance(response, bytes):
        content = response
    else:
        raise TypeError(f"Invalid response: {response!r}")

    return BytesResponse.from_bytes(content, 200, CIMultiDict())
