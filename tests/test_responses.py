import asyncio
import pytest

from view.app import as_app
from view.headers import as_multidict
from view.request import Request
from view.response import Response, ResponseLike
from view.status_codes import BadRequest, Success
from view.testing import AppTestClient, into_tuple


@pytest.mark.asyncio
async def test_str_or_bytes_response():
    class MyString(str):
        pass

    @as_app
    def app(request: Request) -> ResponseLike:
        if request.path == "/":
            return "Hello"
        elif request.path == "/bytes":
            return b"World"
        elif request.path == "/my-string":
            return MyString("My string")
        else:
            raise BadRequest()

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"Hello", 200, {})
    assert (await into_tuple(client.get("/bytes"))) == (b"World", 200, {})
    assert (await into_tuple(client.get("/my-string"))) == (b"My string", 200, {})


@pytest.mark.asyncio
async def test_raw_response():
    @as_app
    def app(request: Request) -> ResponseLike:
        async def stream():
            yield b"Test"

        return Response(
            receive_data=stream,
            status_code=Success.CREATED,
            headers=as_multidict({"hello": "world"}),
        )

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"Test", 201, {"hello": "world"})


@pytest.mark.asyncio
async def test_tuple_response():
    @as_app
    def app(request: Request) -> ResponseLike:
        if request.path == "/status":
            return "Test", Success.CREATED
        elif request.path == "/status-bytes":
            return b"Bytes", Success.CREATED
        elif request.path == "/headers":
            return "Headers", Success.CREATED, {"hello": "world"}
        elif request.path == "/headers-bytes":
            return b"HBytes", Success.OK, {b"1": b"2"}
        else:
            raise BadRequest()

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/status"))) == (b"Test", 201, {})
    assert (await into_tuple(client.get("/status-bytes"))) == (b"Bytes", 201, {})
    assert (await into_tuple(client.get("/headers"))) == (
        b"Headers",
        201,
        {"hello": "world"},
    )
    assert (await into_tuple(client.get("/headers-bytes"))) == (
        b"HBytes",
        200,
        {"1": "2"},
    )

@pytest.mark.asyncio
async def test_stream_response_async():
    @as_app
    async def app(request: Request) -> ResponseLike:
        yield b"This "
        await asyncio.sleep(0)
        yield "Is "
        await asyncio.sleep(0)
        yield b"A "
        await asyncio.sleep(0)
        yield "Test"
        await asyncio.sleep(0)

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"This Is A Test", 200, {})


@pytest.mark.asyncio
async def test_stream_response_sync():
    @as_app
    def app(request: Request) -> ResponseLike:
        yield b"This "
        yield "Is "
        yield b"A "
        yield "Test"

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"This Is A Test", 200, {})
