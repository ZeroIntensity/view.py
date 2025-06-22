from multidict import CIMultiDict

from view.app import BaseApp, Request
from view.response import Response
from view.router import Method


class TestClient:
    """
    Client to test an app.

    This makes no actual HTTP requests, and instead should be used to
    exercise correctness of responses.
    """

    def __init__(self, app: BaseApp) -> None:
        self.app = app

    async def request(
        self, route: str, *, method: Method, headers: dict[str, str] | None = None
    ) -> Response:
        request_data = Request(route, method, headers=CIMultiDict(headers or {}))
        return await self.app.process_request(request_data)

    async def get(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.GET, headers=headers)

    async def post(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.POST, headers=headers)

    async def put(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.PUT, headers=headers)

    async def patch(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.PATCH, headers=headers)

    async def delete(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.DELETE, headers=headers)

    async def connect(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.CONNECT, headers=headers)

    async def options(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.OPTIONS, headers=headers)

    async def trace(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.TRACE, headers=headers)

    async def head(
        self, route: str, *, headers: dict[str, str] | None = None
    ) -> Response:
        return await self.request(route, method=Method.HEAD, headers=headers)
