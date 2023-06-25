# flake8: noqa
# NOTE: anything in this file that is defined solely for typing purposes should be
# prefixed with __ to tell the developer that its not an actual symbol defined by
# the extension module

from typing import Any as __Any, NoReturn as __NoReturn

from view.typing import AsgiDict as __AsgiDict
from view.typing import AsgiReceive as __AsgiReceive
from view.typing import AsgiSend as __AsgiSend
from view.typing import RouteInputDict as __RouteInput
from view.typing import ViewRoute as __ViewRoute
from view.typing import Parser as __Parser

class ViewApp:
    def __init__(self) -> __NoReturn: ...
    async def asgi_app_entry(
        self,
        /,
        scope: __AsgiDict,
        receive: __AsgiReceive,
        send: __AsgiSend,
    ) -> None: ...
    def _get(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
    ) -> None: ...
    def _post(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
    ) -> None: ...
    def _put(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
    ) -> None: ...
    def _patch(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
    ) -> None: ...
    def _delete(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
    ) -> None: ...
    def _options(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        inputs: list[__RouteInput[__Any]],
        errors: dict[int, __ViewRoute],
    ) -> None: ...
    def _set_dev_state(self, /, value: bool) -> None: ...
    def _exc(self, /, status_code: int, handler: __ViewRoute) -> None: ...
    def _supply_parsers(self, /, query: __Parser, json: __Parser) -> None: ...

class Context:
    def __init__(self) -> __NoReturn: ...
    def cookie(self, /, __key: str, __value: str) -> None: ...
