from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterable
from typing import TYPE_CHECKING, Any, Literal, TypeAlias, TypedDict

from typing_extensions import NotRequired

from view.core.headers import asgi_to_headers, headers_to_asgi
from view.core.request import Method, Request, extract_query_parameters

if TYPE_CHECKING:
    from view.core.app import BaseApp

__all__ = ("asgi_for_app",)


class ASGIScopeData(TypedDict):
    version: str
    spec_version: NotRequired[str]


ASGIHeaders: TypeAlias = Iterable[tuple[bytes, bytes]]


class ASGIHttpScope(TypedDict):
    type: Literal["http"]
    asgi: ASGIScopeData
    http_version: str
    method: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: ASGIHeaders
    client: Iterable[tuple[str, int]] | None
    server: Iterable[tuple[str, int | None]] | None
    state: NotRequired[dict[str, Any] | None]


class ASGIBodyMixin(TypedDict):
    body: NotRequired[bytes]
    more_body: NotRequired[bool]


class ASGIHttpReceiveResult(ASGIBodyMixin, TypedDict):
    type: Literal["http.request"]


class ASGIHttpSendStart(TypedDict):
    type: Literal["http.response.start"]
    status: int
    headers: ASGIHeaders
    trailers: NotRequired[bool]


class ASGIHttpSendBody(ASGIBodyMixin, TypedDict):
    type: Literal["http.response.body"]


ASGIHttpReceive: TypeAlias = Callable[[], Awaitable[ASGIHttpReceiveResult]]
ASGIHttpSend: TypeAlias = Callable[
    [ASGIHttpSendStart | ASGIHttpSendBody], Awaitable[None]
]
ASGIProtocol: TypeAlias = Callable[
    [ASGIHttpScope, ASGIHttpReceive, ASGIHttpSend], Awaitable[None]
]


def asgi_for_app(app: BaseApp, /) -> ASGIProtocol:
    """
    Generate an ASGI-compliant callable for a given app, allowing
    it to be executed in an ASGI server.

    Don't use this directly; prefer the :meth:`view.core.app.BaseApp.wsgi`
    method instead.
    """

    async def asgi(
        scope: ASGIHttpScope, receive: ASGIHttpReceive, send: ASGIHttpSend
    ) -> None:
        assert scope["type"] == "http"
        method = Method(scope["method"])
        headers = asgi_to_headers(scope["headers"])

        async def receive_data() -> AsyncIterator[bytes]:
            more_body = True
            while more_body:
                data = await receive()
                assert data["type"] == "http.request"
                yield data.get("body", b"")
                more_body = data.get("more_body", False)

        parameters = extract_query_parameters(scope["query_string"])
        request = Request(
            receive_data, app, scope["path"], method, headers, parameters
        )

        response = await app.process_request(request)
        await send(
            {
                "type": "http.response.start",
                "status": response.status_code,
                "headers": headers_to_asgi(response.headers),
            }
        )
        async for data in response.stream_body():
            await send(
                {"type": "http.response.body", "body": data, "more_body": True}
            )

        await send(
            {"type": "http.response.body", "body": b"", "more_body": False}
        )

    return asgi
