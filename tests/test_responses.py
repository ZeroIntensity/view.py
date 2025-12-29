import asyncio

import aiofiles
import pytest

from view.app import as_app
from view.headers import as_multidict
from view.request import Request
from view.response import FileResponse, Response, ResponseLike, JSONResponse
from view.status_codes import (
    BadRequest,
    HTTPError,
    Success,
    STATUS_STRINGS,
    STATUS_EXCEPTIONS,
)
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


@pytest.mark.asyncio
async def test_file_response():
    async with aiofiles.tempfile.NamedTemporaryFile("w") as file:
        await file.write("A" * 10000)

        @as_app
        def app(request: Request) -> ResponseLike:
            return FileResponse.from_file(
                str(file.name), status_code=Success.CREATED, headers={"hello": "world"}
            )

        client = AppTestClient(app)
        assert (await into_tuple(client.get("/"))) == (
            b"A" * 10000,
            201,
            {"hello": "world", "content-type": "text/plain"},
        )


@pytest.mark.asyncio
async def test_status_codes():
    @as_app
    def app(request: Request) -> ResponseLike:
        if request.path == "/":
            raise BadRequest()
        elif request.path == "/message":
            raise BadRequest("Test")
        else:
            raise RuntimeError()

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"400 Bad Request", 400, {})
    assert (await into_tuple(client.get("/message"))) == (b"Test", 400, {})


@pytest.mark.asyncio
@pytest.mark.parametrize("status_exception", list(STATUS_EXCEPTIONS.values()))
async def test_status_code_strings(status_exception: type[HTTPError]):
    @as_app
    async def app(_: Request) -> ResponseLike:
        raise status_exception()

    client = AppTestClient(app)
    response = await client.get("/")
    assert status_exception.status_code == response.status_code
    message = f"{status_exception.status_code} {STATUS_STRINGS[response.status_code]}"
    assert (await response.body()) == message.encode("utf-8")


@pytest.mark.asyncio
async def test_internal_server_error():
    @as_app
    async def app(_: Request):
        raise Exception("silly")

    client = AppTestClient(app)
    response = await client.get("/")
    assert response.status_code == 500
    output = (await response.body()).decode("utf-8")
    assert "Traceback (most recent call last)" in output
    assert "Exception: silly" in output


@pytest.mark.asyncio
async def test_json_response():
    @as_app
    async def app(_: Request):
        return JSONResponse.from_content({"foo": "bar"})

    client = AppTestClient(app)
    response = await client.get("/")
    assert response.status_code == 200
    assert response.headers == {}
    assert (await response.json()) == {"foo": "bar"}
