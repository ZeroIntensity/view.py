import asyncio
from view import new_app, get

app = new_app()
count = 0

@app.get("/param", cache_rate=10)
async def param():
    global count
    count += 1
    return str(count)

async def main():
    async with app.test() as test:
        results = [(await test.get("/param")).message for _ in range(10)]
        assert all(i == results[0] for i in results)


asyncio.run(main())
