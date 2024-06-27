import asyncio
from view import new_app, WebSocket

app = new_app()

@app.get("/")
async def index():
    ...

async def main():
    async with app.test() as test:
        ...

asyncio.run(main())
