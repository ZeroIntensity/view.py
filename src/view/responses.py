from __future__ import annotations

import mimetypes
import sys
from os import PathLike
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, AsyncIterator, Callable

import asyncio
import json
from dataclasses import dataclass

from view.core.headers import HeadersLike, LowerStr, as_real_headers
from view.core.response import Response
from view.core.response import TextResponse as TextResponse  # noqa: PLC0414
from view.exceptions import InvalidTypeError

__all__ = "FileResponse", "JSONResponse", "TextResponse"

StrPath: TypeAlias = str | PathLike[str]


def _guess_file_type(path: StrPath, /) -> str:
    if sys.version_info >= (3, 13):
        return mimetypes.guess_file_type(path)[0] or "text/plain"

    return mimetypes.guess_type(path)[0] or "text/plain"


async def _read_stream(
    path: StrPath, *, chunk_size: int
) -> AsyncIterator[bytes]:
    file = await asyncio.to_thread(open, path, "rb")
    length = chunk_size
    while length == chunk_size:
        data = await asyncio.to_thread(file.read, chunk_size)
        length = len(data)
        yield data


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
        chunk_size: int = 512,  # This probably needs tuning
        content_type: str | None = None,
    ) -> FileResponse:
        """
        Generate a :class:`FileResponse` from a file path.
        """
        if __debug__ and not isinstance(chunk_size, int):
            raise InvalidTypeError(chunk_size, int)

        multi_map = as_real_headers(headers)
        if "content-type" not in multi_map:
            content_type = content_type or _guess_file_type(path)
            multi_map = multi_map.with_new_value(
                LowerStr("content-type"), content_type
            )

        return cls(
            _read_stream(path, chunk_size=chunk_size),
            status_code,
            multi_map,
            path,
        )


@dataclass(slots=True)
class JSONResponse(Response):
    """
    Response containing JSON data.
    """

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
            receive_data=stream(),
        )
