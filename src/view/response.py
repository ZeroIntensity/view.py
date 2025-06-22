from dataclasses import dataclass
from typing import AnyStr, TypeAlias

from multidict import CIMultiDict


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
