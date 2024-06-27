import asyncio
from view import new_app, get

app = new_app()

@app.get("/")
async def index():
    return b"\x09 \x09"

@app.get("/hi")
async def hi():
    return b"hi", 201, {"test": "test"}

async def main():
    async with app.test() as test:
        assert (await test.get("/")).content == b"\x09 \x09"
        assert (await test.get("/hi")).content == b"hi"

asyncio.run(main())
