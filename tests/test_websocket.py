from ward import raises, test

from view import WebSocket, new_app, websocket


@test("websocket echo server")
async def _():
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


@test("websocket message pairs")
async def _():
    app = new_app()

    @websocket("/")
    async def back_and_forth(ws: WebSocket):
        await ws.accept()
        count = 0

        while True:
            message = await ws.pair(count, tp=int)
            assert message == count
            count += 1

    app.load([back_and_forth])

    async with app.test() as test:
        async with test.websocket("/") as ws:
            for i in range(5):
                num = await ws.receive()
                assert num == str(i)
                await ws.send(num)


@test("websocket message pairs receiving first")
async def _():
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


@test("websocket receiving casts")
async def _():
    app = new_app()

    @app.websocket("/")
    async def casts(ws: WebSocket):
        await ws.accept()

        assert (await ws.receive(tp=int)) == 42
        assert (await ws.receive(tp=dict)) == {"hello": 42}
        assert (await ws.receive(tp=bool)) is True
        assert (await ws.receive(tp=bool)) is False

    async with app.test() as test:
        async with test.websocket("/") as ws:
            await ws.send("42")
            await ws.send('{"hello": 42}')
            await ws.send("1")
            await ws.send("false")
