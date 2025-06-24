import pytest

from view.app import as_app
from view.request import Request
from view.response import Response, ResponseLike
from view.testing import AppTestClient, into_tuple
from view.status_codes import Success

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
            raise RuntimeError()

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"Hello", 200, {})
    assert (await into_tuple(client.get("/bytes"))) == (b"World", 200, {})
    assert (await into_tuple(client.get("/my-string"))) == (b"My string", 200, {})


@pytest.mark.asyncio
async def test_raw_response():
    @as_app
    def app(request: Request) -> ResponseLike:
        async def stream():
            yield b"test"
        return Response(receive_data=stream, status_code=Success.OK, headers={"hello": "world"})
