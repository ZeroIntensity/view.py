import asyncio
from view import new_app
from typing import List, Union, Dict

app = new_app()

@app.get("/dict")
@app.query("test", Dict[str, List[str]])
async def d(test: Dict[str, List[str]]):
    return test["a"][0]

async def main():
    async with app.test() as test:
        print(
            (await test.get("/dict", query={"test": {"a": ["1", "2", "3"]}})
        ).message)
asyncio.run(main())
