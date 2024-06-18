import asyncio
from typing import Union

from src.view import Context, body, new_app, page

app = new_app()

@app.get("/")
@body("name", str)
async def index(name: str):
    return name

async def main():
    async with app.test() as test:
        assert (await test.get("/", body={"name": "hi"})).message == "hi"

asyncio.run(main())
