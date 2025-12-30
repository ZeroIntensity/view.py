from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterable
from typing import IO, TYPE_CHECKING, Any, TypeAlias

from view.core.headers import wsgi_as_multidict
from view.core.request import Method, Request, extract_query_parameters
from view.core.status_codes import STATUS_STRINGS

if TYPE_CHECKING:
    from view.core.app import BaseApp

__all__ = ("wsgi_for_app",)

WSGIHeaders: TypeAlias = list[tuple[str, str]]
# We can't use a TypedDict for the environment because it has arbitrary keys
# for the headers.
WSGIEnvironment: TypeAlias = dict[str, Any]
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
        headers = wsgi_as_multidict(environ)
        parameters = extract_query_parameters(environ["QUERY_STRING"])
        request = Request(stream, app, path, method, headers, parameters)
        response = loop.run_until_complete(app.process_request(request))

        wsgi_headers: WSGIHeaders = []
        for key, value in response.headers.items():
            # Multidict has a weird string subclass as the key for some reason
            wsgi_headers.append((str(key), value))

        # WSGI is such a weird spec
        status_str = f"{response.status_code} {STATUS_STRINGS[response.status_code]}"
        start_response(status_str, wsgi_headers)
        return [loop.run_until_complete(response.body())]

    return wsgi
