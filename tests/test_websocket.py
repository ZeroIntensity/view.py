from ward import raises, test

from view import WebSocket, new_app


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

    @app.websocket("/")
    async def back_and_forth(ws: WebSocket):
        await ws.accept()
        count = 0

        while True:
            message = await ws.pair(count)
            assert message == count
            count += 1

    async with app.test() as test:
        async with test.websocket("/") as ws:
            for i in range(5):
                num = await ws.receive()
                assert num == str(i)
                await ws.send(num)
