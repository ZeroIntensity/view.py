from __future__ import annotations

import mimetypes
import warnings
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from os import PathLike
from typing import AnyStr, Generic, TypeAlias

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

    def __post_init__(self) -> None:
        if __debug__:
            # Avoid circular import issues
            from view.status_codes import STATUS_STRINGS

            if self.status_code not in STATUS_STRINGS:
                raise ValueError(
                    f"{self.status_code!r} is not a valid HTTP status code"
                )

    async def as_tuple(self) -> tuple[bytes, int, RequestHeaders]:
        """
        Process the response as a tuple. This is mainly useful
        for assertions in testing.
        """
        return (await self.body(), self.status_code, self.headers)


# AnyStr isn't working with the type checker, probably because it's a TypeVar
StrOrBytes: TypeAlias = str | bytes
ResponseTuple: TypeAlias = tuple[StrOrBytes, int] | tuple[StrOrBytes, int, HeadersLike]
ResponseLike: TypeAlias = (
    Response | StrOrBytes | AsyncGenerator[StrOrBytes] | Generator[StrOrBytes] | ResponseTuple
)
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
        if __debug__ and not isinstance(chunk_size, int):
            raise TypeError(
                f"expected an integer for chunk_size, but got {chunk_size!r}"
            )

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


def as_bytes(data: str | bytes) -> bytes:
    """
    Utility to convert a string to a byte string, or let a byte string pass.
    """
    if isinstance(data, str):
        return data.encode("utf-8")
    else:
        return data


@dataclass(slots=True)
class StrOrBytesResponse(Response, Generic[AnyStr]):
    """
    Simple in-memory response for a UTF-8 encoded string, or a raw ASCII byte string.
    """

    content: AnyStr

    @classmethod
    def from_content(
        cls,
        content: AnyStr,
        /,
        *,
        status_code: int = 200,
        headers: HeadersLike | None = None,
    ) -> StrOrBytesResponse[AnyStr]:
        """
        Generate a `StringResponse` from a `string` object.
        """

        if __debug__ and not isinstance(content, (str, bytes)):
            raise TypeError(f"Expected a string or bytes object, got {content!r}")

        async def stream() -> AsyncGenerator[bytes]:
            yield as_bytes(content)

        return cls(stream, status_code, as_multidict(headers), content)


def _wrap_response_tuple(response: ResponseTuple) -> Response:
    if response == ():
        raise ValueError("Response cannot be an empty tuple")

    if __debug__ and len(response) == 1:
        warnings.warn(
            f"Returned tuple {response!r} with a single item,"
            " which is useless. Return the item directly.",
            RuntimeWarning,
        )
        return StrOrBytesResponse.from_content(response[0])

    content = response[0]
    status = response[1]
    headers: HeadersLike | None = None

    if len(response) > 2:
        headers = response[2]

    if __debug__ and len(response) > 3:
        raise ValueError(f"Got excess data in response tuple {response[3:]!r}")

    return StrOrBytesResponse.from_content(content, status_code=status, headers=headers)


def wrap_response(response: ResponseLike, /) -> Response:
    """
    Wrap a response from a view into a `Response` object.
    """
    logger.debug(f"Got response: {response!r}")
    if isinstance(response, Response):
        return response
    elif isinstance(response, (str, bytes)):
        return StrOrBytesResponse.from_content(response)
    elif isinstance(response, tuple):
        return _wrap_response_tuple(response)
    elif isinstance(response, AsyncGenerator):

        async def stream() -> AsyncGenerator[bytes]:
            async for data in response:
                yield as_bytes(data)

        return Response(stream, status_code=200, headers=CIMultiDict())
    elif isinstance(response, Generator):
        async def stream() -> AsyncGenerator[bytes]:
            for data in response:
                yield as_bytes(data)

        return Response(stream, status_code=200, headers=CIMultiDict())
    else:
        raise TypeError(f"Invalid response: {response!r}")
