from ward import raises, test

from view import WebSocket, new_app

"""
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
        ws = await test.websocket("/")
        await ws.send("hello")
        assert ws.receive() == "hello"
        await ws.send("world")
        assert ws.receive() == "world"
"""
