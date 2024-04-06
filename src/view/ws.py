from __future__ import annotations

from typing import Union, overload

import ujson
from typing_extensions import Self

from _view import ViewWebSocket, WebSocketHandshakeError, register_ws_cls

__all__ = "WebSocketSendable", "WebSocketReceivable", "WebSocket"

WebSocketSendable = Union[str, bytes, dict, int, bool]
WebSocketReceivable = Union[str, bytes, dict, int, bool]


class WebSocket:
    """Object representing a WebSocket connection."""

    def __init__(self, socket: ViewWebSocket) -> None:
        self.socket: ViewWebSocket = socket
        self.open: bool = False
        self.done: bool = False

    @overload
    async def receive(self, tp: type[str] = str) -> str:
        ...

    @overload
    async def receive(self, tp: type[bytes] = bytes) -> bytes:
        ...

    @overload
    async def receive(self, tp: type[dict] = dict) -> dict:
        ...

    @overload
    async def receive(self, tp: type[int] = int) -> int:
        ...

    @overload
    async def receive(self, tp: type[bool] = bool) -> bool:
        ...

    async def receive(
        self, tp: type[WebSocketReceivable] = str
    ) -> WebSocketReceivable:
        """Receive a message from the WebSocket.

        Args:
            tp: Python type to cast the received message to."""
        if not self.open:
            raise WebSocketHandshakeError(
                "cannot receive from connection that is not open"
            )
        res: str = await self.socket.receive()

        if res is None:
            raise WebSocketHandshakeError("socket disconnected")

        if tp is str:
            return res

        if tp is int:
            return int(res)

        if tp is dict:
            return ujson.loads(res)

        if tp is bytes:
            return res.encode()

        if tp is bool:
            if (res not in {"True", "true", "False", "false"}) and (
                not res.isdigit()
            ):
                raise TypeError(f"{res!r} is not boolean-like")

            if res.isdigit():
                return bool(int(res))

            return res in {"True", "true"}

        raise TypeError(
            f"expected type str, bytes, dict, int, or bool, but got {tp!r}"
        )

    async def send(self, message: WebSocketSendable) -> None:
        """Send a message to the client.

        Args:
            message: Message to send."""
        if not self.open:
            raise WebSocketHandshakeError(
                "cannot send to connection that is not open"
            )
        if isinstance(message, (str, bytes)):
            await self.socket.send(message)
        elif isinstance(message, dict):
            await self.socket.send(ujson.dumps(message))
        elif isinstance(message, int):
            await self.socket.send(str(message))
        elif isinstance(message, bool):
            await self.socket.send("true" if message else "false")
        else:
            raise TypeError(
                f"expected object of type str, bytes, dict, int, or bool, but got {message!r}"
            )

    @overload
    async def pair(
        self,
        message: WebSocketSendable,
        *,
        tp: type[str] = str,
        recv_first: bool = False,
    ) -> str:
        ...

    @overload
    async def pair(
        self,
        message: WebSocketSendable,
        *,
        tp: type[bytes] = bytes,
        recv_first: bool = False,
    ) -> bytes:
        ...

    @overload
    async def pair(
        self,
        message: WebSocketSendable,
        *,
        tp: type[int] = int,
        recv_first: bool = False,
    ) -> int:
        ...

    @overload
    async def pair(
        self,
        message: WebSocketSendable,
        *,
        tp: type[dict] = dict,
        recv_first: bool = False,
    ) -> dict:
        ...

    @overload
    async def pair(
        self,
        message: WebSocketSendable,
        *,
        tp: type[bool] = bool,
        recv_first: bool = False,
    ) -> bool:
        ...

    async def pair(
        self,
        message: WebSocketSendable,
        *,
        tp: type[WebSocketReceivable] = str,
        recv_first: bool = False,
    ) -> WebSocketReceivable:
        """Receive a message and send a message.

        Args:
            message: Message to send. Equivalent to `message` in `send()`
            tp: Type to cast the result to. Equivalent to `tp` in `receive()`
            recv_first: Whether to receive the message before sending. If this is `False`, a message is sent first, then a message is received.
        """
        if not recv_first:
            await self.send(message)
            return await self.receive(tp)
        else:
            res = await self.receive(tp)
            await self.send(message)
            return res

    async def close(self) -> None:
        """Close the connection."""
        if not self.open:
            raise WebSocketHandshakeError(
                "cannot close connection that isn't open"
            )

        self.open = False
        self.done = True
        await self.socket.close()

    async def accept(self) -> None:
        """Open the connection."""
        if self.done or self.open:
            raise WebSocketHandshakeError("connection was already opened")

        self.open = True
        await self.socket.accept()

    recv = receive
    connect = accept

    async def __aenter__(self) -> Self:
        await self.accept()
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()


register_ws_cls(WebSocket)
