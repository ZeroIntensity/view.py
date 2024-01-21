# flake8: noqa
# NOTE: anything in this file that is defined solely for typing purposes should be
# prefixed with __ to tell the developer that its not an actual symbol defined by
# the extension module

from typing import Any as __Any
from typing import Awaitable as __Awaitable
from typing import Coroutine as __Coroutine
from typing import NoReturn as __NoReturn
from typing import TypeVar as __TypeVar

from view.typing import AsgiDict as __AsgiDict
from view.typing import AsgiReceive as __AsgiReceive
from view.typing import AsgiSend as __AsgiSend
from view.typing import Parser as __Parser
from view.typing import Part as __Part
from view.typing import RouteInputDict as __RouteInput
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
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        /,
    ) -> None: ...
    def _post(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        /,
    ) -> None: ...
    def _put(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        /,
    ) -> None: ...
    def _patch(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        /,
    ) -> None: ...
    def _delete(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        /,
    ) -> None: ...
    def _options(
        self,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
        parts: list[__Part | str],
        /,
    ) -> None: ...
    def _set_dev_state(self, value: bool, /) -> None: ...
    def _exc(self, status_code: int, handler: __ViewRoute, /) -> None: ...
    def _supply_parsers(self, query: __Parser, json: __Parser, /) -> None: ...

def test_awaitable(coro: __Coroutine[__Any, __Any, __T], /) -> __Awaitable[__T]: ...
