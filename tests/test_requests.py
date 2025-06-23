import pytest

from view.app import Request, as_app
from view.response import ResponseLike
from view.router import Method
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

    client = AppTestClient(app)
    assert (await into_tuple(client.get("/"))) == (b"Hello", 200, {})
    assert (await into_tuple(client.get("/1", headers={"test-something": "42"}))) == (
        b"World",
        200,
        {},
    )
