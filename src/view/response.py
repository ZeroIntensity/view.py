from dataclasses import dataclass
from typing import AnyStr, TypeAlias

from multidict import CIMultiDict


@dataclass(slots=True, frozen=True)
class Response:
    content: bytes
    status_code: int
    headers: CIMultiDict


ResponseLike: TypeAlias = Response | AnyStr
