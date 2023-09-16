from typing import Union

from ward import test

from view import Response, body, new_app, query


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
        return Response(MyObject(), 201)

    async with app.test() as test:
        assert (await test.get("/")).message == "hello"
        res = await test.get("/multi")
        assert res.message == "hello"
        assert res.status == 201


@test("body type validation")
async def _():
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


@test("query type validation")
async def _():
    app = new_app()

    @app.get("/")
    @query("name", str)
    async def index(name: str):
        return name

    @app.get("/status")
    @query("status", int)
    async def stat(status: int):
        return "hello", status

    @app.get("/union")
    @query("test", bool, int)
    async def union(test: Union[bool, int]):
        if type(test) is bool:
            return "1"
        elif type(test) is int:
            return "2"
        else:
            raise Exception

    @app.get("/multi")
    @query("status", int)
    @query("name", str)
    async def multi(status: int, name: str):
        return name, status

    async with app.test() as test:
        assert (await test.get("/", query={"name": "hi"})).message == "hi"
        assert (await test.get("/status", query={"status": 404})).status == 404
        assert (
            await test.get("/status", query={"status": "hi"})
        ).status == 400  # noqa
        assert (await test.get("/union", query={"test": "a"})).status == 400
        assert (
            await test.get("/union", query={"test": "true"})
        ).message == "1"  # noqa
        assert (await test.get("/union", query={"test": "2"})).message == "2"
        res = await test.get("/multi", query={"status": 404, "name": "test"})
        assert res.status == 404
        assert res.message == "test"


@test("queries directly from app and body")
async def _():
    app = new_app()

    @app.query("name", str)
    @app.get("/")
    async def query_route(name: str):
        return name

    @app.get("/body")
    @app.body("name", str)
    async def body_route(name: str):
        return name

    async with app.test() as test:
        assert (await test.get("/", query={"name": "test"})).message == "test"
        assert (
            await test.get("/body", body={"name": "test"})
        ).message == "test"


@test("response type")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return Response("hello world", 201, {"hello": "world"})

    async with app.test() as test:
        res = await test.get("/")

        assert res.message == "hello world"
        assert res.status == 201
        assert res.headers["hello"] == "world"


@test("non async routes")
async def _():
    app = new_app()

    @app.get("/")
    def index():
        return "hello world", 201, {"a": "b"}

    async with app.test() as test:
        res = await test.get("/")

        assert res.message == "hello world"
        assert res.status == 201
        assert res.headers["a"] == "b"
