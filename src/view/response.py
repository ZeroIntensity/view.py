from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from os import PathLike
from typing import AnyStr, AsyncGenerator, TypeAlias

import aiofiles
from loguru import logger
from multidict import CIMultiDict

from view.body import BodyMixin
from view.request import RequestHeaders

__all__ = "Response", "ResponseLike"


@dataclass(slots=True)
class Response(BodyMixin):
    """
    High-level dataclass representing a response from a view.
    """

    status_code: int
    headers: CIMultiDict[str]

    async def as_tuple(self) -> tuple[bytes, int, RequestHeaders]:
        """
        Process the response as a tuple. This is mainly useful
        for assertions in testing.
        """
        return (await self.body(), self.status_code, self.headers)


HeadersLike = RequestHeaders | dict[str, str] | dict[bytes, bytes]
StrPath: TypeAlias = str | PathLike[str]


def as_multidict(headers: HeadersLike | None, /) -> RequestHeaders:
    """
    Convenience function for casting a "header-like object" (or `None`)
    to a `CIMultiDict`.
    """
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
    """
    Response containing a file, streamed asynchronously.
    """

    path: StrPath

    @classmethod
    def from_file(
        cls,
        path: StrPath,
        /,
        *,
        status_code: int = 200,
        headers: HeadersLike | None = None,
        chunk_size: int = 512,
        content_type: str | None = None,
    ) -> FileResponse:
        """
        Generate a `FileResponse` from a file path.
        """

        async def stream():
            async with aiofiles.open(path, "rb") as file:
                length = chunk_size
                while length == chunk_size:
                    data = await file.read(chunk_size)
                    length = len(data)
                    yield data

        multidict = as_multidict(headers)
        if "content-type" not in multidict:
            content_type = (
                content_type or mimetypes.guess_file_type(path)[0] or "text/plain"
            )
            multidict["content-type"] = content_type

        return cls(stream, status_code, multidict, path)


@dataclass(slots=True)
class BytesResponse(Response):
    """
    Simple in-memory response for a byte string.
    """

    content: bytes

    def as_tuple_sync(self) -> tuple[bytes, int, RequestHeaders]:
        """
        Synchronous variation of `as_tuple`, using the cached content.
        """
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
        """
        Generate a `BytesResponse` from a `bytes` object.
        """

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

    return BytesResponse.from_bytes(content)
