# flake8: noqa
from typing import Any, Awaitable, Callable

_AsgiSerial = (
    bytes
    | str
    | int
    | float
    | list
    | tuple
    | dict[str, "_AsgiSerial"]
    | bool
    | None
)

_AsgiDict = dict[str, _AsgiSerial]

_AsgiReceive = Callable[[], Awaitable[_AsgiDict]]
_AsgiSend = Callable[[_AsgiDict], Awaitable[None]]

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

class ViewApp:
    async def asgi_app_entry(
        self, scope: _AsgiDict, receive: _AsgiReceive, send: _AsgiSend
    ) -> None: ...
    def _get(self, path: str, callable: ViewRoute): ...

PASS_CTX: int = ...
USE_CACHE: int = ...
