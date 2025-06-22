from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from typing import AnyStr, AsyncGenerator, TypeAlias

import aiofiles
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


HeadersLike = CIMultiDict | dict[str, str] | dict[bytes, bytes]
StrOrBytesPath: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]


def as_multidict(headers: HeadersLike | None, /) -> CIMultiDict:
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


@dataclass(slots=True)
class FileResponse(Response):
    path: StrOrBytesPath

    @classmethod
    def from_file(
        cls,
        path: StrOrBytesPath,
        /,
        *,
        status_code: int = 200,
        headers: HeadersLike | None = None,
        increment: int = 512,
    ) -> FileResponse:
        async def stream():
            async with aiofiles.open(path, "rb") as file:
                length = increment
                while length == increment:
                    data = await file.read(increment)
                    length = len(data)
                    yield data

        return cls(stream, status_code, as_multidict(headers), path)


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
        cls,
        content: bytes,
        /,
        *,
        status_code: int = 200,
        headers: HeadersLike | None = None,
    ) -> BytesResponse:
        async def stream() -> AsyncGenerator[bytes]:
            yield content

        return cls(stream, status_code, as_multidict(headers), content)


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
