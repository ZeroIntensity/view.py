from __future__ import annotations

import json
import mimetypes
import sys
import warnings
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from dataclasses import dataclass
from os import PathLike
from typing import Any, AnyStr, Generic, TypeAlias

import aiofiles
from loguru import logger

from view.core.body import BodyMixin
from view.core.headers import HeadersLike, RequestHeaders, as_real_headers
from view.exceptions import InvalidTypeError, ViewError
from view.core.multi_map import MultiMap

__all__ = "Response", "ViewResult", "ResponseLike"


@dataclass(slots=True)
class Response(BodyMixin):
    """
    Low-level dataclass representing a response from a view.
    """

    status_code: int
    headers: RequestHeaders[str]

    def __post_init__(self) -> None:
        if __debug__:
            # Avoid circular import issues
            from view.core.status_codes import STATUS_STRINGS

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
_ResponseTuple: TypeAlias = (
    tuple[StrOrBytes, int] | tuple[StrOrBytes, int, HeadersLike]
)
ResponseLike: TypeAlias = (
    Response
    | StrOrBytes
    | AsyncGenerator[StrOrBytes]
    | Generator[StrOrBytes]
    | _ResponseTuple
)
ViewResult = ResponseLike | Awaitable[ResponseLike]
StrPath: TypeAlias = str | PathLike[str]


def _guess_file_type(path: StrPath, /) -> str:
    if sys.version_info >= (3, 13):
        return mimetypes.guess_file_type(path)[0] or "text/plain"

    return mimetypes.guess_type(path)[0] or "text/plain"


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
            raise InvalidTypeError(chunk_size, int)

        async def stream():
            async with aiofiles.open(path, "rb") as file:
                length = chunk_size
                while length == chunk_size:
                    data = await file.read(chunk_size)
                    length = len(data)
                    yield data

        multi_map = as_real_headers(headers)
        if "content-type" not in multi_map:
            content_type = content_type or _guess_file_type(path)
            multi_map["content-type"] = content_type

        return cls(stream, status_code, multi_map, path)


def _as_bytes(data: str | bytes) -> bytes:
    """
    Utility to convert a string to a byte string, or let a byte string pass.
    """
    if isinstance(data, str):
        return data.encode("utf-8")

    return data


@dataclass(slots=True)
class TextResponse(Response, Generic[AnyStr]):
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
    ) -> TextResponse[AnyStr]:
        """
        Generate a `TextResponse` from either a `str` or `bytes` object.
        """

        if __debug__ and not isinstance(content, (str, bytes)):
            raise InvalidTypeError(content, str, bytes)

        async def stream() -> AsyncGenerator[bytes]:
            yield _as_bytes(content)

        return cls(stream, status_code, as_real_headers(headers), content)


@dataclass(slots=True)
class JSONResponse(Response):
    content: dict[str, Any]
    parsed_data: str

    @classmethod
    def from_content(
        cls,
        content: dict[str, Any],
        *,
        parse_function: Callable[[dict[str, Any]], str] = json.dumps,
        status_code: int = 200,
        headers: HeadersLike | None = None,
    ) -> JSONResponse:
        data = parse_function(content)

        async def stream() -> AsyncGenerator[bytes]:
            yield data.encode("utf-8")

        return cls(
            content=content,
            parsed_data=data,
            headers=as_real_headers(headers),
            status_code=status_code,
            receive_data=stream,
        )


class InvalidResponseError(ViewError):
    """
    A view returned an object that view.py doesn't know how to convert into a
    response object.
    """


def _wrap_response_tuple(response: _ResponseTuple) -> Response:
    if __debug__ and response == ():
        raise InvalidResponseError("Response cannot be an empty tuple")

    if __debug__ and len(response) == 1:
        warnings.warn(
            f"Returned tuple {response!r} with a single item,"
            " which is useless. Return the item directly.",
            RuntimeWarning,
            stacklevel=2,
        )
        return TextResponse.from_content(response[0])

    content = response[0]
    if __debug__ and isinstance(content, Response):
        raise InvalidResponseError(
            "Response() objects cannot be used with response"
            " tuples. Instead, use the status_code and/or headers parameter(s)."
        )

    status = response[1]
    headers: HeadersLike | None = None

    # Ruff wants me to use a constant here, but I think this is clear enough
    # for lengths.
    if len(response) > 2:  # noqa
        headers = response[2]

    if __debug__ and len(response) > 3:  # noqa
        raise InvalidResponseError(
            f"Got excess data in response tuple {response[3:]!r}"
        )

    return TextResponse.from_content(
        content, status_code=status, headers=headers
    )


def _wrap_response(response: ResponseLike, /) -> Response:
    """
    Wrap a response from a view into a `Response` object.
    """
    logger.debug(f"Got response: {response!r}")
    if isinstance(response, Response):
        return response

    if isinstance(response, (str, bytes)):
        return TextResponse.from_content(response)

    if isinstance(response, tuple):
        return _wrap_response_tuple(response)

    if isinstance(response, AsyncGenerator):

        async def stream() -> AsyncGenerator[bytes]:
            async for data in response:
                yield _as_bytes(data)

        return Response(stream, status_code=200, headers=MultiMap())

    if isinstance(response, Generator):

        async def stream() -> AsyncGenerator[bytes]:
            for data in response:
                yield _as_bytes(data)

        return Response(stream, status_code=200, headers=MultiMap())

    raise TypeError(f"Invalid response: {response!r}")


async def wrap_view_result(result: ViewResult, /) -> Response:
    """
    Turn the raw result of a view, which might be a coroutine, into a usable
    `Response` object.
    """
    if isinstance(result, Awaitable):
        result = await result

    return _wrap_response(result)
