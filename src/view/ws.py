"""
view.py WebSocket APIs

It's unlikely that you need something from this module for anything other than typing purposes.
The bulk of the WebSocket implementation is C code, and considered unstable.
"""
from __future__ import annotations

from types import TracebackType
from typing import Any, Union, overload

import ujson
from typing_extensions import Self

from _view import ViewWebSocket

from ._logging import Service
from .exceptions import (
    WebSocketDisconnectError,
    WebSocketExpectError,
    WebSocketHandshakeError,
)

__all__ = "WebSocketSendable", "WebSocketReceivable", "WebSocket"

WebSocketSendable = Union[str, bytes, dict, int, bool]
WebSocketReceivable = Union[str, bytes, dict, int, bool]


class WebSocket:
    """
    Object representing a WebSocket connection.

    It's highly unlikely that you need to create an instance of this class yourself!
    The constructor of this class is considered unstable, do not expect API stability!

    This class should only be directly referenced when using type hints.
    """

    def __init__(self, socket: ViewWebSocket) -> None:
        self._socket: ViewWebSocket = socket
        self.open: bool = False
        """Whether the connection is currently open."""
        self.done: bool = False
        """Whether the connection was accepted, and then closed."""

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

    async def receive(self, tp: type[WebSocketReceivable] = str) -> WebSocketReceivable:
        """
        Receive a message from the client.

        Args:
            tp: Python type to cast the received message to. Supported types are `str`, `bytes`, `dict` (as JSON), `int`, and `bool`.

        Raises:
            WebSocketHandshakeError: The connection has already been closed.
            WebSocketDisconnectError: The connection closed while receiving.
            WebSocketExpectError: The received data could not be casted to the requested type.

        Example:
            ```py
            from view import websocket, WebSocket

            @websocket("/")
            async def index(ws: WebSocket):
                await ws.accept()
                message = await ws.receive()
            ```
        """
        if not self.open:
            raise WebSocketHandshakeError(
                "cannot receive from connection that is not open"
            )
        res: str = await self._socket.receive()

        if res is None:
            raise WebSocketDisconnectError("socket disconnected")

        if tp is str:
            return res

        if tp is int:
            return int(res)

        if tp is dict:
            return ujson.loads(res)

        if tp is bytes:
            return res.encode()

        if tp is bool:
            if (res not in {"True", "true", "False", "false"}) and (not res.isdigit()):
                raise WebSocketExpectError(
                    f"expected boolean-like message, got {res!r}"
                )

            if res.isdigit():
                return bool(int(res))

            return res in {"True", "true"}

        raise TypeError(f"expected type str, bytes, dict, int, or bool, but got {tp!r}")

    async def send(self, message: WebSocketSendable) -> None:
        """
        Send a message to the client.

        Args:
            message: Message to send to the client.

        Raises:
            WebSocketHandshakeError: The connection has already been closed.
            TypeError: Type of `message` cannot be sent to the client.

        Example:
            ```py
            from view import websocket, WebSocket

            @websocket("/")
            async def index(ws: WebSocket):
                await ws.accept()
                await ws.send("Hello from the other side")
            ```
        """
        if not self.open:
            raise WebSocketHandshakeError("cannot send to connection that is not open")
        if isinstance(message, (str, bytes)):
            await self._socket.send(message)
        elif isinstance(message, dict):
            await self._socket.send(ujson.dumps(message))
        elif isinstance(message, bool):
            await self._socket.send("true" if message else "false")
        elif isinstance(message, int):
            await self._socket.send(str(message))
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
        """
        Receive a message and send a message.

        Args:
            message: Message to send. Equivalent to `message` in `send()`
            tp: Type to cast the result to. Equivalent to `tp` in `receive()`
            recv_first: Whether to receive the message before sending. If this is `False`, a message is sent first, then a message is received.

        Example:
            ```py
            from view import websocket, WebSocket

            @websocket("/")
            async def index(ws: WebSocket):
                await ws.accept()
                response = await ws.pair("syn")
                assert response == "ack"
            ```
        """
        if not recv_first:
            await self.send(message)
            return await self.receive(tp)
        else:
            res = await self.receive(tp)
            await self.send(message)
            return res

    async def close(self) -> None:
        """
        Close the connection.

        Raises:
            WebSocketHandshakeError: The connection has already been closed.

        Example:
            ```py
            from view import websocket, WebSocket

            @websocket("/")
            async def index(ws: WebSocket):
                # ...
                await ws.close()  # Close the connection
            ```
        """
        if not self.open:
            raise WebSocketHandshakeError("cannot close connection that isn't open")

        self.open = False
        self.done = True
        await self._socket.close()

    async def accept(self) -> None:
        """
        Open the connection.

        Raises:
            WebSocketHandshakeError: `accept()` has already been called on this object.


        Example:
            ```py
            from view import websocket, WebSocket

            @websocket("/")
            async def index(ws: WebSocket):
                await ws.accept()  # Open the connection
                # ...
            ```
        """
        if self.done or self.open:
            raise WebSocketHandshakeError("connection was already opened")

        self.open = True
        await self._socket.accept()

    async def expect(self, message: WebSocketSendable) -> None:
        msg = await self.receive(tp=type(message))
        if msg != message:
            raise WebSocketExpectError(f"websocket expected {message!r}, got {msg!r}")

    recv = receive
    connect = accept

    async def __aenter__(self) -> Self:
        await self.accept()
        return self

    async def __aexit__(
        self,
        tp: type[BaseException] | BaseException | None,
        val: Any,
        tb: TracebackType | None,
    ) -> None:
        if tp == WebSocketDisconnectError:
            self.open = False
            Service.warning("Unhandled WebSocket disconnect")
        elif tp:
            self.open = False
            # exception occurred, raise it so view.py can handle it
            raise
        elif self.open:
            await self.close()
