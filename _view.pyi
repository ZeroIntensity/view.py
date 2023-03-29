# flake8: noqa
# NOTE: anything in this file that is defined solely for typing purposes should be
# prefixed with __ to tell the developer that its not an actual symbol defined by
# the extension module

from typing import Any as __Any
from typing import Callable as __Callable
from typing import TypedDict as __TypedDict

from view.typing import AsgiDict as __AsgiDict
from view.typing import AsgiReceive as __AsgiReceive
from view.typing import AsgiSend as __AsgiSend
from view.typing import RouteInputDict as __RouteInput
from view.typing import ViewRoute as __ViewRoute

class ViewApp:
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
        query: list[__RouteInput[__Any]],
        body: list[__RouteInput[__Any]],
    ) -> None: ...
    def _post(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        query: list[__RouteInput[__Any]],
        body: list[__RouteInput[__Any]],
    ) -> None: ...
    def _put(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        query: list[__RouteInput[__Any]],
        body: list[__RouteInput[__Any]],
    ) -> None: ...
    def _patch(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        query: list[__RouteInput[__Any]],
        body: list[__RouteInput[__Any]],
    ) -> None: ...
    def _delete(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        query: list[__RouteInput[__Any]],
        body: list[__RouteInput[__Any]],
    ) -> None: ...
    def _options(
        self,
        /,
        path: str,
        callable: __ViewRoute,
        cache_rate: int,
        query: list[__RouteInput[__Any]],
        body: list[__RouteInput[__Any]],
    ) -> None: ...
    def _set_dev_state(self, /, value: bool) -> None: ...
