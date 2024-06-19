import asyncio
from typing import Union

from src.view import Context, body, new_app, page

app = new_app()

@app.get("/")
@app.context
async def index(ctx: Context):
    print(ctx.cookies)
    return "a"

async def main():
    async with app.test() as test:
        await test.get("/", headers={"cookie": "hello=world"})

asyncio.run(main())
