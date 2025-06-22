import contextlib
import contextvars
from abc import ABC, abstractmethod
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Callable, Iterator, Literal, TypeAlias, TypeVar, overload

from multidict import CIMultiDict

from view.response import Response, ResponseLike
from view.router import Method, Route, RouteHandler, Router
from view.status_codes import HTTPError, NotFound

__all__ = "BaseApp", "Request"

RouteHandlerVar = TypeVar("RouteHandlerVar", bound=RouteHandler)
RouteDecorator: TypeAlias = Callable[[RouteHandlerVar], RouteHandlerVar]


@dataclass(slots=True, frozen=True)
class Request:
    path: str
    headers: CIMultiDict


def wrap_response(response: ResponseLike) -> Response:
    """
    Wrap a response from a handler into a `Response` object.
    """
    if isinstance(response, Response):
        return response

    content: bytes
    if isinstance(response, str):
        content = response.encode()
    elif isinstance(response, bytes):
        content = response
    else:
        raise TypeError(f"Invalid response: {response!r}")

    return Response(content, 200, CIMultiDict())


class BaseApp(ABC):
    """Base view.py application."""

    def __init__(self, *, router: Router):
        self._request = contextvars.ContextVar[Request](
            "The current request being handled."
        )
        self.router = router

    @contextlib.contextmanager
    def request_context(self, request: Request) -> Iterator[None]:
        """
        Enter a context for the given request.
        """
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
        """
        Get the current request being handled.
        """
        if validate:
            return self._request.get()

        try:
            return self._request.get()
        except LookupError:
            return None

    @abstractmethod
    async def process_request(self, request: Request) -> Response:
        """
        Get the response from the server for a given request.
        """

    def wsgi(self): ...

    def asgi(self): ...

    def run(self): ...


class RoutableApp(BaseApp):
    def __init__(self) -> None:
        super().__init__(router=Router())

    async def _execute_handler(self, handler: RouteHandler) -> ResponseLike:
        try:
            result = handler()
            if isinstance(result, Awaitable):
                result = await result

            return result
        except HTTPError as error:
            http_error = type(error)
            handler = self.router.lookup_error(http_error)
            return await self._execute_handler(handler)

    async def process_request(self, request: Request) -> Response:
        """
        Get the response from the server for a given request.
        """
        route: Route | None = self.router.lookup_route(request.path)
        handler: RouteHandler
        if route is None:
            handler = self.router.lookup_error(NotFound)
        else:
            handler = route.handler

        with self.request_context(request):
            response = await self._execute_handler(handler)

        return wrap_response(response)

    def route(self, path: str, /, *, method: Method) -> RouteDecorator:
        """
        Decorator interface for adding a route to the app.
        """

        def decorator(handler: RouteHandlerVar, /) -> RouteHandlerVar:
            self.router.push_route(handler, path, method)
            return handler

        return decorator

    def get(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.GET)

    def post(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.POST)

    def put(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.PUT)

    def patch(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.PATCH)

    def delete(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.DELETE)

    def connect(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.CONNECT)

    def options(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.OPTIONS)

    def trace(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.TRACE)

    def head(self, path: str, /) -> RouteDecorator:
        return self.route(path, method=Method.HEAD)

    def error(self, status: int | type[HTTPError], /) -> RouteDecorator:
        def decorator(handler: RouteHandlerVar, /) -> RouteHandlerVar:
            self.router.push_error(status, handler)
            return handler

        return decorator
