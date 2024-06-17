import pytest
from leaks import limit_leaks

from view import (InvalidRouteError, WebSocket, WebSocketExpectError,
                  WebSocketHandshakeError, new_app, websocket)


@pytest.mark.asyncio
@limit_leaks("1 MB")
async def test_websocket_echo_server():
    app = new_app()

    @app.websocket("/")
    async def echo(ws: WebSocket):
        await ws.accept()

        while True:
            message = await ws.receive()
            await ws.send(message)

    async with app.test() as test:
        async with test.websocket("/") as ws:
            await ws.send("hello")
            assert (await ws.receive()) == "hello"
            await ws.send("world")
            assert (await ws.receive()) == "world"


@pytest.mark.asyncio
@limit_leaks("1 MB")
async def test_websocket_message_pairs():
    app = new_app()

    @websocket("/")
    async def back_and_forth(ws: WebSocket):
        await ws.accept()
        count = 0

        while True:
            message = await ws.pair(count, tp=int)
            assert message == count
            count += 1

    app.load(back_and_forth)

    async with app.test() as test:
        async with test.websocket("/") as ws:
            for i in range(5):
                num = await ws.receive()
                assert num == str(i)
                await ws.send(num)


@pytest.mark.asyncio
@limit_leaks("1 MB")
async def test_websocket_message_pairs_receiving_first():
    app = new_app()

    @app.websocket("/")
    async def forth_and_back(ws: WebSocket):
        await ws.accept()

        for i in range(5):
            assert i == await ws.pair(i, recv_first=True, tp=int)

    async with app.test() as test:
        async with test.websocket("/") as ws:
            count = 0
            await ws.send(str(count))
            assert (await ws.receive()) == str(count)
            count += 1


@pytest.mark.asyncio
@limit_leaks("1 MB")
async def test_websocket_receiving_casts():
    app = new_app()

    @app.websocket("/")
    async def casts(ws: WebSocket):
        await ws.accept()

        assert (await ws.receive(tp=int)) == 42
        assert (await ws.receive(tp=dict)) == {"hello": 42}
        assert (await ws.receive(tp=bool)) is True
        assert (await ws.receive(tp=bool)) is False
        assert (await ws.receive(tp=bytes)) == b"test"

        await ws.send("hi")
        await ws.expect("foo")
        await ws.expect(b"foo")

        with pytest.raises(WebSocketExpectError):
            await ws.expect(1)

    async with app.test() as test:
        async with test.websocket("/") as ws:
            await ws.send("42")
            await ws.send('{"hello": 42}')
            await ws.send("1")
            await ws.send("false")
            await ws.send("test")

            assert (await ws.receive()) == "hi"
            await ws.send("foo")
            await ws.send("bar")
            await ws.send("2")


@pytest.mark.asyncio
@limit_leaks("1 MB")
async def test_websocket_handshake_errors():
    app = new_app()

    @app.websocket("/")
    async def casts(ws: WebSocket):
        with pytest.raises(WebSocketHandshakeError):
            await ws.send("hi")

        with pytest.raises(WebSocketHandshakeError):
            await ws.receive()

        async with ws:
            with pytest.raises(WebSocketHandshakeError):
                await ws.accept()
            await ws.send("test")

        with pytest.raises(WebSocketHandshakeError):
            await ws.accept()

        with pytest.raises(WebSocketHandshakeError):
            await ws.close()

        with pytest.raises(WebSocketHandshakeError):
            await ws.send("hi")

        with pytest.raises(WebSocketHandshakeError):
            await ws.receive()

    async with app.test() as test:
        async with test.websocket("/") as ws:
            assert (await ws.receive()) == "test"


def test_disallow_body_inputs():
    app = new_app()

    @app.websocket("/")
    @app.body("foo", str)
    async def whatever(ws: WebSocket, foo: str): ...

    with pytest.raises(InvalidRouteError):
        app.load()

@limit_leaks("1 MB")
@pytest.mark.asyncio
async def test_websocket_leaks():
    app = new_app()

    @app.websocket("/")
    async def index(ws: WebSocket):
        await ws.accept()
        await ws.close()

    async with app.test() as test:
        for i in range(10000):
            async with test.websocket("/") as ws:
                ...
