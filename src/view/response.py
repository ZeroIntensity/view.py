from __future__ import annotations

from contextlib import suppress
import mimetypes
from collections.abc import AsyncIterator
from dataclasses import dataclass
from os import PathLike
from typing import AnyStr, AsyncGenerator, Generic, TypeAlias
import warnings

import aiofiles
from loguru import logger
from multidict import CIMultiDict

from view.body import BodyMixin
from view.headers import HeadersLike, RequestHeaders, as_multidict

__all__ = "Response", "ResponseLike"


@dataclass(slots=True)
class Response(BodyMixin):
    """
    Low-level dataclass representing a response from a view.
    """

    status_code: int
    headers: CIMultiDict[str]

    async def as_tuple(self) -> tuple[bytes, int, RequestHeaders]:
        """
        Process the response as a tuple. This is mainly useful
        for assertions in testing.
        """
        return (await self.body(), self.status_code, self.headers)


ResponseLike: TypeAlias = Response | AnyStr | AsyncIterator[AnyStr]
StrPath: TypeAlias = str | PathLike[str]


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
class StringOrBytesResponse(Response, Generic[AnyStr]):
    """
    Simple in-memory response for a UTF-8 encoded string, or a raw ASCII byte string.
    """
    content: AnyStr

    @classmethod
    def from_content(cls, content: AnyStr, /, *, status_code: int = 200, headers: HeadersLike | None = None) -> StringOrBytesResponse:
        """
        Generate a `StringResponse` from a `string` object.
        """
        
        if __debug__ and not isinstance(content, (str, bytes)):
            raise TypeError(f"expected a string or bytes object, got {content!r}")

        async def stream() -> AsyncGenerator[bytes]:
            if isinstance(content, str):
                yield content.encode("utf-8")
            else:
                yield content

        return cls(stream, status_code, as_multidict(headers), content)


def _wrap_response_tuple(response: tuple[str | bytes, int, HeadersLike]) -> Response:
    if response == ():
        raise ValueError("Response cannot be an empty tuple")

    if __debug__ and len(response) == 1:
        warnings.warn(f"Returned tuple {response!r} with a single item,"
                      " which is useless. Return the item directly.",
                      RuntimeWarning)

    content = response[0]
    status = response[1]
    headers: HeadersLike | None = None

    with suppress(KeyError):
        headers = response[2]

    return StringOrBytesResponse.from_content(content, status_code=status, headers=headers)


def wrap_response(response: ResponseLike, /) -> Response:
    """
    Wrap a response from a view into a `Response` object.
    """
    logger.debug(f"Got response: {response!r}")
    if isinstance(response, Response):
        return response
    elif isinstance(response, (str, bytes)):
        return StringOrBytesResponse.from_content(response)
    elif isinstance(response, tuple):
        return _wrap_response_tuple(response)
    elif isinstance(response, AsyncIterator):

        async def stream() -> AsyncIterator[bytes]:
            async for data in response:
                yield data

        return Response(stream, status_code=200, headers=CIMultiDict())
    else:
        raise TypeError(f"Invalid response: {response!r}")
