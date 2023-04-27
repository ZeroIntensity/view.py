from __future__ import annotations

from typing import Any, Awaitable, Callable, ClassVar, Generic, TypeVar

from typing_extensions import ParamSpec, Protocol, TypedDict

AsgiSerial = (
    bytes
    | str
    | int
    | float
    | list
    | tuple
    | dict[str, "AsgiSerial"]
    | bool
    | None
)

AsgiDict = dict[str, AsgiSerial]

AsgiReceive = Callable[[], Awaitable[AsgiDict]]
AsgiSend = Callable[[AsgiDict], Awaitable[None]]

ResponseHeaders = dict[str, str]

_ViewResponseTupleA = tuple[str, int, ResponseHeaders]
_ViewResponseTupleB = tuple[int, str, ResponseHeaders]
_ViewResponseTupleC = tuple[str, ResponseHeaders, int]
_ViewResponseTupleD = tuple[int, ResponseHeaders, str]
_ViewResponseTupleE = tuple[ResponseHeaders, str, int]
_ViewResponseTupleF = tuple[ResponseHeaders, int, str]
_ViewResponseTupleG = tuple[str, ResponseHeaders]
_ViewResponseTupleH = tuple[ResponseHeaders, str]
_ViewResponseTupleI = tuple[str, int]
_ViewResponseTupleJ = tuple[int, str]

_ViewResponseType = (
    _ViewResponseTupleA
    | _ViewResponseTupleB
    | _ViewResponseTupleC
    | _ViewResponseTupleD
    | _ViewResponseTupleE
    | _ViewResponseTupleF
    | _ViewResponseTupleG
    | _ViewResponseTupleH
    | _ViewResponseTupleI
    | _ViewResponseTupleJ
    | str
)
P = ParamSpec("P")
V = TypeVar("V", bound="ValueType")

ViewResponse = Awaitable[_ViewResponseType]
Context = Any
R = TypeVar("R", bound="ViewResponse")
ViewRoute = Callable[P, R]


class BodyLike(Protocol):
    __view_body__: ClassVar[dict[str, ValueType]]


ValueType = BodyLike | str | int | dict[str, "ValueType"] | bool | float
ValidatorResult = bool | tuple[bool, str]
Validator = Callable[[V], ValidatorResult]


class RouteInputDict(TypedDict, Generic[V]):
    name: str
    type: type[V] | None
    default: V | None
    validators: list[Validator[V]]
    is_body: bool


ViewBodyType = str | int | dict | bool | float
ViewBody = dict[str, ViewBodyType]


class _SupportsViewBodyCV(Protocol):
    __view_body__: ViewBody


class _SupportsViewBodyF(Protocol):
    def __view_body__(self) -> ViewBody:
        ...


class _SupportsAnnotations(Protocol):
    __annotations__: ClassVar[dict[str, Any]]


SupportsViewBody = _SupportsViewBodyCV | _SupportsViewBodyF
ViewBodyLike = SupportsViewBody | _SupportsAnnotations
