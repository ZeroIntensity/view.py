from typing import AsyncIterator

import pytest

from view.app import App, as_app
from view.headers import as_multidict
from view.request import Method, Request
from view.response import ResponseLike
from view.status_codes import BadRequest
from view.testing import AppTestClient, into_tuple


@pytest.mark.asyncio
async def test_request_data():
    @as_app
    def app(request: Request) -> ResponseLike:
        assert request.app == app
        assert request.app.current_request() is request
        assert isinstance(request.path, str)
        assert request.method is Method.GET

        if request.path == "/":
            assert request.headers == {}
            return "Hello"
        elif request.path == "/1":
            assert request.headers == {"test-something": "42"}
            return "World"
        else:
            raise BadRequest()

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"Hello", 200, {})
    assert (await into_tuple(client.get("/1", headers={"test-something": "42"}))) == (
        b"World",
        200,
        {},
    )


@pytest.mark.asyncio
async def test_manual_request():
    @as_app
    def app(request: Request) -> ResponseLike:
        assert request.app == app
        assert request.app.current_request() is request
        assert isinstance(request.path, str)
        assert request.method is Method.POST
        assert request.headers["test"] == "42"

        return "1"

    async def stream_none() -> AsyncIterator[bytes]:
        yield b""

    with pytest.raises(LookupError):
        app.current_request()

    manual_request = Request(
        receive_data=stream_none,
        app=app,
        path="/",
        method=Method.POST,
        headers=as_multidict({"test": "42"}),
    )
    response = await app.process_request(manual_request)
    assert (await response.body()) == b"1"


@pytest.mark.asyncio
async def test_request_body():
    @as_app
    async def app(request: Request) -> ResponseLike:
        body = await request.body()
        if request.path == "/":
            assert body == b"test"
            return "1"
        elif request.path == "/large":
            assert body == b"A" * 10000
            return "2"
        else:
            raise BadRequest()

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/", body=b"test"))) == (b"1", 200, {})
    assert (await into_tuple(client.get("/large", body=b"A" * 10000))) == (
        b"2",
        200,
        {},
    )


@pytest.mark.asyncio
async def test_request_headers():
    @as_app
    async def app(request: Request) -> ResponseLike:
        if request.path == "/":
            assert request.headers["foo"] == "42"
            return "1"
        elif request.path == "/many":
            assert request.headers["Bar"] == "42"
            assert request.headers["bar"] == "42"
            assert request.headers["baR"] == "42"
            assert request.headers["test"] == "123"
            return "2"
        else:
            raise BadRequest()

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/", headers={"foo": "42"}))) == (b"1", 200, {})
    assert (
        await into_tuple(
            client.get("/many", headers={"Bar": "24", "bAr": "42", "test": "123"})
        )
    ) == (b"2", 200, {})


@pytest.mark.asyncio
async def test_request_router():
    app = App()

    @app.get("/")
    def index():
        return "Index"

    @app.get("/hello")
    def hello():
        return "Hello"

    @app.get("/hello/world")
    def world():
        return "World"

    @app.get("/goodbye/world")
    def goodbye():
        return "Goodbye"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"Index", 200, {})
    assert (await into_tuple(client.get("/hello"))) == (b"Hello", 200, {})
    assert (await into_tuple(client.get("/hello/world"))) == (b"World", 200, {})
    assert (await into_tuple(client.get("/"))) == (b"Index", 200, {})
    assert (await into_tuple(client.get("/goodbye/world"))) == (b"Goodbye", 200, {})


@pytest.mark.asyncio
async def test_request_path_parameters():
    app = App()

    @app.get("/")
    def index():
        return "Index"

    @app.get("/spanish/{inquisition}")
    async def path_param():
        request = app.current_request()
        assert request.parameters["inquisition"] == "42"
        return "0"

    @app.get("/spanish/inquisition")
    def overwrite_path_param():
        return "1"

    @app.get("/spanish/inquisition/{nobody}")
    def sub_path_param():
        request = app.current_request()
        assert request.parameters["nobody"] == "gotcha"
        return "2"

    @app.get("/spanish/{inquisition}/{nobody}")
    def double_path_param():
        request = app.current_request()
        assert request.parameters["inquisition"] == "1"
        assert request.parameters["nobody"] == "2"
        return "3"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/spanish/42"))) == (b"0", 200, {})
    assert (await into_tuple(client.get("/spanish/inquisition"))) == (b"1", 200, {})
    assert (await into_tuple(client.get("/spanish/inquisition/gotcha"))) == (
        b"2",
        200,
        {},
    )
    assert (await into_tuple(client.get("/spanish/1/2"))) == (b"3", 200, {})


@pytest.mark.asyncio
async def test_request_method():
    app = App()

    @app.get("/")
    async def index_get():
        return "get"

    @app.post("/")
    async def index_post():
        return "post"

    @app.patch("/")
    async def index_patch():
        return "patch"

    @app.put("/")
    async def index_put():
        return "put"

    @app.delete("/")
    async def index_delete():
        return "delete"

    @app.connect("/")
    async def index_connect():
        return "connect"

    @app.options("/")
    async def index_options():
        return "options"

    @app.trace("/")
    async def index_trace():
        return "trace"

    @app.head("/")
    async def index_head():
        return "head"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"get", 200, {})
    assert (await into_tuple(client.post("/"))) == (b"post", 200, {})
    assert (await into_tuple(client.patch("/"))) == (b"patch", 200, {})
    assert (await into_tuple(client.put("/"))) == (b"put", 200, {})
    assert (await into_tuple(client.delete("/"))) == (b"delete", 200, {})
    assert (await into_tuple(client.connect("/"))) == (b"connect", 200, {})
    assert (await into_tuple(client.options("/"))) == (b"options", 200, {})
    assert (await into_tuple(client.trace("/"))) == (b"trace", 200, {})
    assert (await into_tuple(client.head("/"))) == (b"head", 200, {})


@pytest.mark.asyncio
async def test_normalized_routes():
    app = App()

    @app.get("")
    async def index():
        return "1"

    @app.get("hello/")
    async def hello():
        return "2"

    @app.get("/test/")
    async def test():
        return "3"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"1", 200, {})
    assert (await into_tuple(client.get(""))) == (b"1", 200, {})
    assert (await into_tuple(client.get("/hello"))) == (b"2", 200, {})
    assert (await into_tuple(client.get("/hello/"))) == (b"2", 200, {})
    assert (await into_tuple(client.get("hello/"))) == (b"2", 200, {})
    assert (await into_tuple(client.get("/test"))) == (b"3", 200, {})
    assert (await into_tuple(client.get("/test/"))) == (b"3", 200, {})
    assert (await into_tuple(client.get("test/"))) == (b"3", 200, {})
