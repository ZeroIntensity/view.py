# flake8: noqa
from typing import Awaitable, Callable

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

class ViewApp:
    async def asgi_app_entry(
        self, scope: _AsgiDict, receive: _AsgiReceive, send: _AsgiSend
    ) -> None: ...
