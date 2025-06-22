from multidict import CIMultiDict
from dataclasses import dataclass
from typing import TypeAlias, AnyStr

@dataclass(slots=True, frozen=True)
class Response:
    content: bytes
    status_code: int
    headers: CIMultiDict

ResponseLike: TypeAlias = Response | AnyStr
