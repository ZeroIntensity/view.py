from __future__ import annotations

from typing import Any, Awaitable, Callable, ClassVar, Generic, TypeVar

from typing_extensions import Protocol, TypedDict

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
ViewResponse = Awaitable[_ViewResponseType]
Context = Any
ViewRoute = Callable[[], ViewResponse]

V = TypeVar("V", bound="ValueType")


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
