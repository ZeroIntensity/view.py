import pytest
from view.response import ResponseLike
from view.router import Method
from view.testing import AppTestClient
from view.app import Request, as_app


@pytest.mark.asyncio
async def test_str_or_bytes_response():
    class MyString(str):
        pass

    @as_app
    def app(request: Request) -> ResponseLike:
        assert request.app == app
        assert request.app.current_request() is request
        assert isinstance(request.path, str)
        assert request.method is Method.GET

        if request.path == "/":
            return "Hello"
        elif request.path == "/bytes":
            return b"World"
        elif request.path == "/my-string":
            return MyString("My string")
        else:
            raise RuntimeError()

    client = AppTestClient(app)
    assert (await client.get("/")).as_tuple() == (b"Hello", 200, {})
    assert (await client.get("/bytes")).as_tuple() == (b"World", 200, {})
    assert (await client.get("/my-string")).as_tuple() == (b"My string", 200, {})
