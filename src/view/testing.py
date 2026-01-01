from __future__ import annotations

from typing import TYPE_CHECKING

from view.core.headers import HeadersLike, as_real_headers
from view.core.request import Method, Request, extract_query_parameters
from view.core.status_codes import STATUS_STRINGS

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable

    from view.core.app import BaseApp
    from view.core.headers import HTTPHeaders
    from view.core.response import Response

__all__ = ("AppTestClient",)


async def into_tuple(
    response_coro: Awaitable[Response], /
) -> tuple[bytes, int, HTTPHeaders]:
    """
    Convenience function for transferring a test client call into a tuple
    through a single ``await``.
    """
    response = await response_coro
    body = await response.body()
    return (body, response.status_code, response.headers)


def ok(body: str | bytes) -> tuple[bytes, int, dict[str, str]]:
    """
    Utility function for an OK response from `into_tuple()`.
    """

    if isinstance(body, str):
        body = body.encode("utf-8")
    return (body, 200, {})


def bad(status_code: int) -> tuple[bytes, int, dict[str, str]]:
    """
    Utility function for an error response from `into_tuple()`.
    """
    body = STATUS_STRINGS[status_code]
    return (f"{status_code} {body}".encode(), status_code, {})


class AppTestClient:
    """
    Client to test an app.

    This makes no actual HTTP requests, and instead should be used to
    exercise correctness of responses.
    """

    def __init__(self, app: BaseApp) -> None:
        self.app = app

    async def request(
        self,
        route: str,
        *,
        method: Method,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        async def stream() -> AsyncGenerator[bytes]:
            yield body or b""

        path, _, query_string = route.partition("?")

        request_data = Request(
            receive_data=stream,
            app=self.app,
            path=path,
            method=method,
            headers=as_real_headers(headers),
            query_parameters=extract_query_parameters(query_string),
        )
        return await self.app.process_request(request_data)

    async def get(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.GET, headers=headers, body=body
        )

    async def post(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.POST, headers=headers, body=body
        )

    async def put(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.PUT, headers=headers, body=body
        )

    async def patch(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.PATCH, headers=headers, body=body
        )

    async def delete(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.DELETE, headers=headers, body=body
        )

    async def connect(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.CONNECT, headers=headers, body=body
        )

    async def options(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.OPTIONS, headers=headers, body=body
        )

    async def trace(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.TRACE, headers=headers, body=body
        )

    async def head(
        self,
        route: str,
        *,
        headers: HeadersLike | None = None,
        body: bytes | None = None,
    ) -> Response:
        return await self.request(
            route, method=Method.HEAD, headers=headers, body=body
        )
