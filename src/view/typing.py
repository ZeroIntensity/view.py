from __future__ import annotations

from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Dict, Generic,
                    List, Literal, Tuple, Type, TypeVar, Union)

from typing_extensions import Concatenate, ParamSpec, Protocol, TypedDict

if TYPE_CHECKING:
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
ResponseBody = Union[str, bytes]

_ViewResponseTupleA = Tuple[ResponseBody, int, ResponseHeaders]
_ViewResponseTupleB = Tuple[int, ResponseBody, ResponseHeaders]
_ViewResponseTupleC = Tuple[ResponseBody, ResponseHeaders, int]
_ViewResponseTupleD = Tuple[int, ResponseHeaders, ResponseBody]
_ViewResponseTupleE = Tuple[ResponseHeaders, ResponseBody, int]
_ViewResponseTupleF = Tuple[ResponseHeaders, int, ResponseBody]
_ViewResponseTupleG = Tuple[ResponseBody, ResponseHeaders]
_ViewResponseTupleH = Tuple[ResponseHeaders, ResponseBody]
_ViewResponseTupleI = Tuple[ResponseBody, int]
_ViewResponseTupleJ = Tuple[int, ResponseBody]

T = TypeVar("T")
MaybeAwaitable = Union[T, Awaitable[T]]

class SupportsViewResult(Protocol):
    def __view_result__(self) -> MaybeAwaitable[ViewResult]: ...


ViewResult = Union[
    _ViewResponseTupleA,
    _ViewResponseTupleB,
    _ViewResponseTupleC,
    _ViewResponseTupleD,
    _ViewResponseTupleE,
    _ViewResponseTupleF,
    _ViewResponseTupleG,
    _ViewResponseTupleH,
    _ViewResponseTupleI,
    _ViewResponseTupleJ,
    ResponseBody,
    SupportsViewResult,
    None,
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
    def __view_body__() -> ViewBody: ...


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
