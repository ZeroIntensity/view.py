from __future__ import annotations

from collections.abc import Sequence
from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Dict, Generic,
                    List, Literal, Tuple, Type, TypeVar, Union)

from typing_extensions import Concatenate, ParamSpec, Protocol, TypedDict

if TYPE_CHECKING:
    from _view import Context

    from .app import RouteDoc
    from .ws import WebSocket

AsgiSerial = Union[
    bytes,
    str,
    int,
    float,
    list,
    tuple,
    Dict[str, "AsgiSerial"],
    bool,
    None,
]

AsgiDict = Dict[str, AsgiSerial]

AsgiReceive = Callable[[], Awaitable[AsgiDict]]
AsgiSend = Callable[[AsgiDict], Awaitable[None]]

RawResponseHeader = Tuple[bytes, bytes]
ResponseHeaders = Union[
    Dict[str, str],
    List[RawResponseHeader],
    Tuple[RawResponseHeader, ...],
]
StrResponseBody = Union[str, bytes]

T = TypeVar("T")
MaybeAwaitable = Union[T, Awaitable[T]]


class SupportsViewResult(Protocol):
    def __view_result__(self, ctx: Context) -> MaybeAwaitable[ViewResult]:
        ...


ResponseBody = Union[StrResponseBody, SupportsViewResult]

ViewResult = Union[
    ResponseBody,
    None,
    Tuple[ResponseBody, int],
    Tuple[ResponseBody, int, dict[str, str]],
    Tuple[ResponseBody, int, Sequence[Tuple[bytes, bytes]]],
]
P = ParamSpec("P")
V = TypeVar("V", bound="ValueType")


ViewResponse = Awaitable[ViewResult]
R = TypeVar("R", bound="ViewResponse")
WebSocketRoute = Callable[Concatenate["WebSocket", P], Awaitable[None]]
ViewRoute = Union[Callable[P, Union[ViewResponse, ViewResult]], WebSocketRoute]


ValidatorResult = Union[bool, Tuple[bool, str]]
Validator = Callable[[V], ValidatorResult]

TypeObject = Union[Type[Any], None]
TypeInfo = Union[
    Tuple[int, TypeObject, List["TypeInfo"]],
    Tuple[int, TypeObject, List["TypeInfo"], Any],
]


class RouteInputDict(TypedDict, Generic[V]):
    name: str
    type_codes: list[TypeInfo]
    default: V | None
    validators: list[Validator[V]]
    is_body: bool
    has_default: bool


ViewBody = Dict[str, "ValueType"]


class _SupportsViewBodyCV(Protocol):
    __view_body__: ViewBody


class _SupportsViewBodyF(Protocol):
    @staticmethod
    def __view_body__() -> ViewBody:
        ...


ViewBodyLike = Union[_SupportsViewBodyCV, _SupportsViewBodyF]
ValueType = Union[
    ViewBodyLike,
    str,
    int,
    Dict[str, "ValueType"],
    bool,
    float,
    Any,
]
Parser = Callable[[str], ViewBody]


class Part(Protocol[V]):
    name: str
    tp: type[V] | None


Callback = Callable[[], Any]
SameSite = Literal["strict", "lax", "none"]
BodyTranslateStrategy = Literal["str", "repr", "result", "custom"]

DocsType = Dict[Tuple[Union[str, Tuple[str, ...]], str], "RouteDoc"]
LogLevel = Literal["debug", "info", "warning", "error", "critical"]
FileWriteMethod = Literal["only", "never", "both"]
StrMethod = Literal[
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "WEBSOCKET",
]
TemplateEngine = Literal["view", "jinja", "django", "mako", "chameleon"]
StrMethodASGI = Literal[
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
CallNext = Callable[[], ViewResponse]
Middleware = Callable[Concatenate[CallNext, P], ViewResponse]
ErrorStatusCode = Literal[
    400,
    401,
    402,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    421,
    422,
    423,
    424,
    425,
    426,
    428,
    429,
    431,
    451,
    500,
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    510,
    511,
]
