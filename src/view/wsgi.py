from __future__ import annotations

import asyncio
from typing import IO, TYPE_CHECKING, Callable, Iterable, TypeAlias

from multidict import CIMultiDict

from view.request import Method, Request
from view.status_codes import STATUS_STRINGS

if TYPE_CHECKING:
    from view.app import BaseApp

WSGIHeaders: TypeAlias = list[tuple[str, str]]
WSGIEnvironment: TypeAlias = dict[str, str | IO[bytes]]  # XXX: Use a TypedDict?
WSGIStartResponse = Callable[[str, WSGIHeaders], Callable[[bytes], object]]
WSGIProtocol: TypeAlias = Callable[
    [WSGIEnvironment, WSGIStartResponse], Iterable[bytes]
]


def wsgi_for_app(
    app: BaseApp,
    /,
    loop: asyncio.AbstractEventLoop | None = None,
    chunk_size: int = 512,
) -> WSGIProtocol:
    """
    Generate a WSGI-compliant callable for a given app, allowing
    it to be executed in an ASGI server.
    """
    loop = loop or asyncio.new_event_loop()

    def wsgi(
        environ: WSGIEnvironment, start_response: WSGIStartResponse
    ) -> Iterable[bytes]:
        method = Method(environ["REQUEST_METHOD"])
        headers = CIMultiDict()

        for key, value in environ.items():
            if not key.startswith("HTTP_"):
                continue

            assert isinstance(value, str)
            key = key.lstrip("HTTP_")
            headers[key.replace("_", "-").lower()] = value

        async def stream():
            request_body: str | IO[bytes] = environ["wsgi.input"]
            assert isinstance(request_body, IO)
            length = chunk_size

            while length == chunk_size:
                data = await asyncio.to_thread(request_body.read, chunk_size)
                length = len(data)
                yield data

        path = environ["PATH_INFO"]
        assert isinstance(path, str)
        request = Request(stream, app, path, method, headers)
        response = loop.run_until_complete(app.process_request(request))

        wsgi_headers: WSGIHeaders = []
        for key, value in response.headers.items():
            wsgi_headers.append((key, value))

        # WSGI is such a weird spec
        status_str = f"{response.status_code} {STATUS_STRINGS[response.status_code]}"
        start_response(status_str, wsgi_headers)
        return [loop.run_until_complete(response.body())]

    return wsgi
