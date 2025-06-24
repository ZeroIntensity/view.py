import pytest

from view.app import as_app, App
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
        assert request.parameters['inquisition'] == '42'
        return "0"

    @app.get("/spanish/inquisition")
    def overwrite_path_param():
        return "1"
    
    @app.get("/spanish/inquisition/{nobody}")
    def sub_path_param():
        request = app.current_request()
        assert request.parameters["nobody"] == 'gotcha'
        return "2"

    @app.get("/spanish/{inquisition}/{nobody}")
    def double_path_param():
        request = app.current_request()
        assert request.parameters["inquisition"] == '1'
        assert request.parameters["nobody"] == '2'
        return "3"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/spanish/42"))) == (b"0", 200, {})
    assert (await into_tuple(client.get("/spanish/inquisition"))) == (b"1", 200, {})
    assert (await into_tuple(client.get("/spanish/inquisition/gotcha"))) == (b"2", 200, {})
    assert (await into_tuple(client.get("/spanish/1/2"))) == (b"3", 200, {})

