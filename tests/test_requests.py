import json
from collections.abc import AsyncIterator

import pytest
from multidict import MultiDict

from view.core.app import App, as_app
from view.core.body import InvalidJSON
from view.core.headers import as_multidict
from view.core.request import Method, Request
from view.core.response import ResponseLike
from view.core.router import DuplicateRoute
from view.status_codes import BadRequest
from view.testing import AppTestClient, into_tuple


def ok(body: str | bytes) -> tuple[bytes, int, dict[str, str]]:
    if isinstance(body, str):
        body = body.encode("utf-8")
    return (body, 200, {})


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
    assert (await into_tuple(client.get("/"))) == ok("Hello")
    assert (await into_tuple(client.get("/1", headers={"test-something": "42"}))) == ok(
        "World"
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
        query_parameters=MultiDict(),
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
    assert (await into_tuple(client.get("/", body=b"test"))) == ok("1")
    assert (await into_tuple(client.get("/large", body=b"A" * 10000))) == ok("2")


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
    assert (await into_tuple(client.get("/", headers={"foo": "42"}))) == ok("1")
    assert (
        await into_tuple(
            client.get("/many", headers={"Bar": "24", "bAr": "42", "test": "123"})
        )
    ) == ok("2")


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
    assert (await into_tuple(client.get("/"))) == ok("Index")
    assert (await into_tuple(client.get("/hello"))) == ok("Hello")
    assert (await into_tuple(client.get("/hello/world"))) == ok("World")
    assert (await into_tuple(client.get("/"))) == ok("Index")
    assert (await into_tuple(client.get("/goodbye/world"))) == ok("Goodbye")


@pytest.mark.asyncio
async def test_request_path_parameters():
    app = App()

    @app.get("/")
    def index():
        return "Index"

    @app.get("/spanish/{inquisition}")
    async def path_param():
        request = app.current_request()
        assert request.path_parameters["inquisition"] == "42"
        return "0"

    @app.get("/spanish/inquisition")
    def overwrite_path_param():
        return "1"

    @app.get("/spanish/inquisition/{nobody}")
    def sub_path_param():
        request = app.current_request()
        assert request.path_parameters["nobody"] == "gotcha"
        return "2"

    @app.get("/spanish/{inquisition}/{nobody}")
    def double_path_param():
        request = app.current_request()
        assert request.path_parameters["inquisition"] == "1"
        assert request.path_parameters["nobody"] == "2"
        return "3"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/spanish/42"))) == ok("0")
    assert (await into_tuple(client.get("/spanish/inquisition"))) == ok("1")
    assert (await into_tuple(client.get("/spanish/inquisition/gotcha"))) == ok("2")
    assert (await into_tuple(client.get("/spanish/1/2"))) == ok("3")


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
    assert (await into_tuple(client.get("/"))) == ok("get")
    assert (await into_tuple(client.post("/"))) == ok("post")
    assert (await into_tuple(client.patch("/"))) == ok("patch")
    assert (await into_tuple(client.put("/"))) == ok("put")
    assert (await into_tuple(client.delete("/"))) == ok("delete")
    assert (await into_tuple(client.connect("/"))) == ok("connect")
    assert (await into_tuple(client.options("/"))) == ok("options")
    assert (await into_tuple(client.trace("/"))) == ok("trace")
    assert (await into_tuple(client.head("/"))) == ok("head")


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
    assert (await into_tuple(client.get("/"))) == ok("1")
    assert (await into_tuple(client.get(""))) == ok("1")
    assert (await into_tuple(client.get("/hello"))) == ok("2")
    assert (await into_tuple(client.get("/hello/"))) == ok("2")
    assert (await into_tuple(client.get("hello/"))) == ok("2")
    assert (await into_tuple(client.get("/test"))) == ok("3")
    assert (await into_tuple(client.get("/test/"))) == ok("3")
    assert (await into_tuple(client.get("test/"))) == ok("3")


@pytest.mark.asyncio
async def test_current_app():
    app = App()

    @app.get("/")
    async def index():
        assert App.current_app() is app
        return "1"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == ok("1")


@pytest.mark.asyncio
async def test_route_division():
    app = App()

    @app.get("/test/main")
    async def main():
        return "1"

    @app.get(main / "foo")
    async def foo():
        return "2"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/test/main/"))) == ok("1")
    assert (await into_tuple(client.get("/test/main/foo"))) == ok("2")


@pytest.mark.asyncio
async def test_request_json():
    app = App()

    @app.get("/")
    async def main():
        request = app.current_request()
        try:
            data = await request.json()
        except InvalidJSON as error:
            raise BadRequest() from error
        return data["test"]

    json_body = json.dumps({"test": "123"}).encode("utf-8")
    client = AppTestClient(app)
    assert (await into_tuple(client.get("/", body=json_body))) == ok("123")
    assert (await into_tuple(client.get("/", body=b"..."))) == (
        b"400 Bad Request",
        400,
        {},
    )


@pytest.mark.asyncio
async def test_request_query_parameters():
    app = App()

    @app.get("/")
    async def main():
        request = app.current_request()
        assert request.query_parameters["foo"] == "bar"
        # FIXME: Why doesn't multidict work?
        # assert request.query_parameters["test"] == ["1", "2", "3"]
        assert "noexist" not in request.query_parameters

        return "ok"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/?foo=bar&test=1&test=2&test=3"))) == ok("ok")


@pytest.mark.asyncio
async def test_subrouters():
    app = App()

    @app.subrouter("/foo/bar")
    async def main(path: str) -> ResponseLike:
        return path

    @app.get("/foo/bar")
    async def conflict() -> ResponseLike:
        return "test"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/foo/bar"))) == ok("test")
    assert (await into_tuple(client.get("/foo/bar/baz"))) == ok("baz")
    assert (await into_tuple(client.get("/foo/bar//baz"))) == ok("/baz")
    assert (await into_tuple(client.get("/foo/bar/"))) == ok("test")
    assert (await into_tuple(client.get("/foo/"))) == (b"404 Not Found", 404, {})

    with pytest.raises(DuplicateRoute):
        app.subrouter("/foo/bar")(main)

    with pytest.raises(DuplicateRoute):
        app.get("/foo/bar")(conflict.view)

    with pytest.raises(RuntimeError):
        app.subrouter("/{test}/x")(main)
