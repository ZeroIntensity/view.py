import contextlib
import contextvars
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Literal, overload

from multidict import CIMultiDict

from view.response import Response, ResponseLike
from view.router import Route, RouteHandler, Router
from view.status_codes import HTTPError, NotFound

__all__ = "App", "Request"


@dataclass(slots=True, frozen=True)
class Request:
    path: str
    headers: CIMultiDict


def wrap_response(response: ResponseLike) -> Response:
    if isinstance(response, Response):
        return response

    content: bytes
    if isinstance(response, str):
        content = response.encode()
    elif isinstance(response, bytes):
        content = response
    else:
        raise TypeError(f"")

    return Response(content, 200, CIMultiDict())


class App(Router):
    def __init__(self):
        self._request = contextvars.ContextVar[Request](
            "The current request being handled."
        )

    async def execute_handler(self, handler: RouteHandler) -> ResponseLike:
        result = handler()
        if isinstance(result, Awaitable):
            result = await result

        return result

    def default_error(self, error: type[HTTPError]) -> RouteHandler:
        """
        Get the default server error handler for a given HTTP error.
        """

        def inner():
            return Response(
                b"Error", status_code=error.status_code, headers=CIMultiDict()
            )

        return inner

    @contextlib.contextmanager
    def _request_context(self, request: Request):
        token = self._request.set(request)
        try:
            yield
        finally:
            self._request.reset(token)

    @overload
    def current_request(self, *, validate: Literal[False]) -> Request | None: ...

    @overload
    def current_request(self, *, validate: Literal[True]) -> Request: ...

    def current_request(self, *, validate: bool = True) -> Request | None:
        if validate:
            return self._request.get()

        try:
            return self._request.get()
        except LookupError:
            return None

    async def process_request(self, request: Request) -> Response:
        route: Route | None = self.lookup_route(request.path)
        handler: RouteHandler
        if route is None:
            handler = self.lookup_error(NotFound) or self.default_error(NotFound)
        else:
            handler = route.handler

        with self._request_context(request):
            response = await self.execute_handler(handler)

        return wrap_response(response)
