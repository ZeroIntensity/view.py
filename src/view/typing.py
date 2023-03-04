from typing import Any, Awaitable, Callable

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
ViewRouteContext = Callable[[Context], ViewResponse]
ViewRouteNull = Callable[[], ViewResponse]
ViewRoute = ViewRouteContext | ViewRouteNull
