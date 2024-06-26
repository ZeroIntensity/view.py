import asyncio
from view import new_app, body    
from typing import Union

app = new_app()

@app.get("/")
@body("name", str)
async def index(name: str):
    return name

@app.get("/status")
@body("status", int)
async def stat(status: int):
    return "hello", status

@app.get("/union")
@body("test", bool, int)
async def union(test: Union[bool, int]):
    if type(test) is bool:
        return "1"
    elif type(test) is int:
        return "2"
    else:
        raise Exception

@app.get("/multi")
@body("status", int)
@body("name", str)
async def multi(status: int, name: str):
    return name, status

async def main():
    async with app.test() as test:
        assert (await test.get("/", body={"name": "hi"})).message == "hi"
        assert (await test.get("/status", body={"status": 404})).status == 404
        assert (
            await test.get("/status", body={"status": "hi"})
        ).status == 400  # noqa
        assert (await test.get("/union", body={"test": "a"})).status == 400
        assert (
            await test.get("/union", body={"test": "true"})
        ).message == "1"  # noqa
        assert (await test.get("/union", body={"test": "2"})).message == "2"
        res = await test.get("/multi", body={"status": 404, "name": "test"})
        assert res.status == 404
        assert res.message == "test"

asyncio.run(main())
