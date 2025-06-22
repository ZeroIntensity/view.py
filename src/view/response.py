from dataclasses import dataclass
from typing import AnyStr, TypeAlias

from loguru import logger
from multidict import CIMultiDict

__all__ = "Response", "ResponseLike"


@dataclass(slots=True, frozen=True)
class Response:
    """
    High-level dataclass representing a response from a view.
    """

    content: bytes
    status_code: int
    headers: CIMultiDict

    def as_tuple(self) -> tuple[bytes, int, CIMultiDict]:
        """
        Process the response as a tuple. This is mainly useful
        for assertions in testing.
        """
        return (self.content, self.status_code, self.headers)


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

    return Response(content, 200, CIMultiDict())
