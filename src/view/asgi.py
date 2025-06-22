from __future__ import annotations

from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Iterable,
    Literal,
    NotRequired,
    TypeAlias,
    TypedDict,
)
from multidict import CIMultiDict

from view.app import BaseApp
from view.request import Method, Request

__all__ = ("asgi_for_app",)


class ASGIScopeData(TypedDict):
    version: str
    spec_version: NotRequired[str]


ASGIHeaders = Iterable[tuple[bytes, bytes]]


class ASGIHttpScope(TypedDict):
    type: Literal["http"]
    asgi: ASGIScopeData
    http_version: str
    method: str
    scheme: str
    path: str
    raw_path: bytes
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

def headers_as_multidict(headers: ASGIHeaders, /) -> CIMultiDict:
    """
    Convert ASGI headers to a case-insensitive multidict.
    """
    multidict = CIMultiDict()

    for key, value in headers:
        multidict[key.decode("utf-8")] = value.decode("utf-8")

    return multidict


def multidict_as_headers(headers: CIMultiDict, /) -> ASGIHeaders:
    """
    Convert a case-insensitive multidict to an ASGI header iterable.
    """
    asgi_headers: ASGIHeaders = []

    for key, value in headers:
        asgi_headers.append((key.encode("utf-8"), value.encode("utf-8")))

    return asgi_headers


def asgi_for_app(app: BaseApp, /) -> ASGIProtocol:
    """
    Generate an ASGI-compliant callable for a given app, allowing
    it to be executed in an ASGI server.
    """
    async def asgi(
        scope: ASGIHttpScope, receive: ASGIHttpReceive, send: ASGIHttpSend
    ) -> None:
        assert scope["type"] == "http"
        method = Method(scope["method"])
        headers = headers_as_multidict(scope["headers"])

        async def receive_data() -> AsyncIterator[bytes]:
            more_body = True
            while more_body:
                data = await receive()
                assert data["type"] == "http.request"
                yield data.get("body", b"")
                more_body = data.get("more_body", False)

        request = Request(receive_data, app, scope["path"], method, headers)

        response = await app.process_request(request)
        await send(
            {
                "type": "http.response.start",
                "status": response.status_code,
                "headers": multidict_as_headers(response.headers),
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
