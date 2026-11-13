"""
Implementation and utilities for running view.py applications on an ASGI server.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterable
from typing import IO, TYPE_CHECKING, Any, TypeAlias

from view.core.headers import headers_to_wsgi, wsgi_to_headers
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
    loop: asyncio.AbstractEventLoop,
    chunk_size: int = 512,
) -> WSGIProtocol:
    """
    Generate a WSGI-compliant callable for a given app, allowing
    it to be executed in an ASGI server.

    Don't use this directly; prefer the :meth:`view.core.app.BaseApp.wsgi`
    method instead.
    """

    def wsgi(
        environ: WSGIEnvironment, start_response: WSGIStartResponse
    ) -> Iterable[bytes]:
        async def _async_wrapper() -> Iterable[bytes]:
            method = Method(environ["REQUEST_METHOD"])

            async def stream():
                request_body: str | IO[bytes] = environ["wsgi.input"]
                assert isinstance(request_body, IO)
                length = chunk_size

                while length == chunk_size:
                    data = await asyncio.to_thread(
                        request_body.read, chunk_size
                    )
                    length = len(data)
                    yield data

            path = environ["PATH_INFO"]
            assert isinstance(path, str)
            headers = wsgi_to_headers(environ)
            parameters = extract_query_parameters(environ["QUERY_STRING"])
            request = Request(stream(), app, path, method, headers, parameters)
            response = await app.process_request(request)

            wsgi_headers: WSGIHeaders = headers_to_wsgi(response.headers)

            # WSGI is such a weird spec
            status_str = f"{response.status_code} {STATUS_STRINGS[response.status_code]}"
            start_response(status_str, wsgi_headers)
            return [await response.body()]

        response = asyncio.run_coroutine_threadsafe(_async_wrapper(), loop)
        return response.result()

    return wsgi
