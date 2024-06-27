import asyncio
from view import new_app, Context
from view.exceptions import WebSocketExpectError

app = new_app()

@app.get("/")
@app.query("a", str)
@app.context
@app.body("c", str)
async def index(a: str, ctx: Context, c: str):
    b = ctx.headers["b"]
    assert isinstance(b, str)
    return a + b + c

async def main():

    async with app.test() as test:
        assert (
            await test.get(
                "/", query={"a": "a"}, headers={"b": "b"}, body={"c": "c"}
            )
        ).message == "abc"
asyncio.run(main())
