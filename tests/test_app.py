from ward import test

from view import new_app


@test("responses")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return "hello"

    async with app.test() as test:
        assert (await test.get("/")).message == "hello"


@test("status codes")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return "error", 400

    async with app.test() as test:
        res = await test.get("/")
        assert res.status == 400
        assert res.message == "error"

@test("headers")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return "hello", {"a": "b"}

    async with app.test() as test:
        res = await test.get("/")
        assert res.headers["a"] == "b"
        assert res.message == "hello"


@test("combination of headers, responses, and status codes")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return 201, "123", {"a": "b"}

    async with app.test() as test:
        res = await test.get("/")
        assert res.status == 201
        assert res.message == "123"
        assert res.headers["a"] == "b"


@test("result protocol")
async def _():
    app = new_app()

    class MyObject:
        def __view_result__(self) -> str:
            return "hello"

    @app.get("/")
    async def index():
        return MyObject()

    @app.get("/multi")
    async def multi():
        return 201, MyObject()

    async with app.test() as test:
        assert (await test.get("/")).message == "hello"
        res = await test.get("/multi")
        assert res.message == "hello"
        assert res.status == 201
