# flake8: noqa
# NOTE: anything in this file that is defined solely for typing purposes should be
# prefixed with __ to tell the developer that its not an actual symbol defined by
# the extension module
from typing import TypeVar as __TypeVar

from view.typing import AsgiDict as __AsgiDict
from view.typing import AsgiReceive as __AsgiReceive
from view.typing import AsgiSend as __AsgiSend
from view.typing import ViewRoute as __ViewRoute

__T_ViewRoute = __TypeVar("__T_ViewRoute", bound=__ViewRoute)

class ViewApp:
    async def asgi_app_entry(
        self, /, scope: __AsgiDict, receive: __AsgiReceive, send: __AsgiSend
    ) -> None: ...
    def _get(self, /, path: str, callable: __T_ViewRoute) -> __T_ViewRoute: ...

PASS_CTX: int = ...
USE_CACHE: int = ...
