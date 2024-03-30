# flake8: noqa
# NOTE: anything in this file that is defined solely for typing purposes should be
# prefixed with __ to tell the developer that its not an actual symbol defined by
# the extension module

from ipaddress import IPv4Address as __IPv4Address
from ipaddress import IPv6Address as __IPv6Address
from typing import Any as __Any
from typing import Awaitable as __Awaitable
from typing import Callable as __Callable
from typing import Coroutine as __Coroutine
from typing import Iterable as __Iterable
from typing import Literal as __Literal
from typing import NoReturn as __NoReturn
from typing import TypeVar as __TypeVar

from view.routing import RouteData as __RouteData
from view.typing import AsgiDict as __AsgiDict
from view.typing import AsgiReceive as __AsgiReceive
from view.typing import AsgiSend as __AsgiSend
from view.typing import Middleware as __Middleware
from view.typing import Parser as __Parser
from view.typing import Part as __Part
from view.typing import RouteInputDict as __RouteInput
from view.typing import StrMethodASGI as __StrMethodASGI
from view.typing import TypeInfo as __TypeInfo
from view.typing import ViewRoute as __ViewRoute

__T = __TypeVar("__T")

class ViewApp:
    def __init__(self) -> __NoReturn: ...
    async def asgi_app_entry(
        self,
        scope: __AsgiDict,
        receive: __AsgiReceive,
        send: __AsgiSend,
        /,
    ) -> None: ...
    def _get(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any] | __RouteData],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        middleware: list[__Middleware],
        /,
    ) -> None: ...
    def _post(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any] | __RouteData],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        middleware: list[__Middleware],
        /,
    ) -> None: ...
    def _put(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any] | __RouteData],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        middleware: list[__Middleware],
        /,
    ) -> None: ...
    def _patch(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any] | __RouteData],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        middleware: list[__Middleware],
        /,
    ) -> None: ...
    def _delete(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any] | __RouteData],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        middleware: list[__Middleware],
        /,
    ) -> None: ...
    def _options(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any] | __RouteData],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        middleware: list[__Middleware],
        /,
    ) -> None: ...
    def _websocket(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any] | __RouteData],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        middleware: list[__Middleware],
        /,
    ) -> None: ...
    def _set_dev_state(self, value: bool, /) -> None: ...
    def _exc(self, status_code: int, handler: __ViewRoute, /) -> None: ...
    def _supply_parsers(self, query: __Parser, json: __Parser, /) -> None: ...
    def _register_error(self, error: type, /) -> None: ...

def test_awaitable(coro: __Coroutine[__Any, __Any, __T], /) -> __Awaitable[__T]: ...

class Context:
    def __init__(self) -> __NoReturn: ...

    cookies: dict[str, str]
    headers: dict[str, str]
    client: __IPv4Address | __IPv6Address | None
    server: __IPv4Address | __IPv6Address | None
    method: __StrMethodASGI
    path: str
    scheme: __Literal["http", "https"]
    http_version: __Literal["1.0", "1.1", "2.0", "view_test"]

class TCPublic:
    def _compile(
        self,
        iterable: __Iterable[__TypeInfo],
        json_parser: __Callable[[str], dict],
        /,
    ) -> None: ...
    def _cast(self, obj: object, allow_cast: bool, /) -> __Any: ...

class ViewWebSocket:
    def __init__(self) -> __NoReturn: ...
    async def accept(self) -> None: ...
    async def send(self, text: str | bytes, /) -> None: ...
    async def close(self) -> None: ...
    async def receive(self) -> str: ...

class InvalidStatusError(RuntimeError): ...
class WebSocketHandshakeError(RuntimeError): ...

def setup_route_log(func: __Callable[[int | str, str, str], None]) -> None: ...
def register_ws_cls(tp: type[__Any]) -> None: ...
