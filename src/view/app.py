from __future__ import annotations

import contextlib
import contextvars
from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import Callable, Iterator, Literal, TypeAlias, TypeVar, overload

from loguru import logger

from view.asgi import ASGIProtocol, asgi_for_app
from view.request import Method, Request
from view.response import Response, ResponseLike, wrap_response
from view.router import Route, Router, RouteView
from view.status_codes import HTTPError, InternalServerError, NotFound

__all__ = "BaseApp", "as_app", "App"

RouteViewVar = TypeVar("RouteViewVar", bound=RouteView)
RouteDecorator: TypeAlias = Callable[[RouteViewVar], RouteViewVar]


class BaseApp(ABC):
    """Base view.py application."""

    def __init__(self):
        self._request = contextvars.ContextVar[Request](
            "The current request being handled."
        )

    @contextlib.contextmanager
    def request_context(self, request: Request) -> Iterator[None]:
        """
        Enter a context for the given request.
        """
        with logger.contextualize(request=request):
            token = self._request.set(request)
            try:
                yield
            finally:
                self._request.reset(token)

    @overload
    def current_request(
        self, *, validate: Literal[False]
    ) -> Request | None: ...

    @overload
    def current_request(
        self, *, validate: Literal[True] = True
    ) -> Request: ...

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

    def asgi(self) -> ASGIProtocol:
        return asgi_for_app(self)

    def run(self): ...


SingleView = Callable[[Request], ResponseLike]


class SingleViewApp(BaseApp):
    """
    Application with a single view function that
    processes all requests.
    """

    def __init__(self, view: SingleView) -> None:
        super().__init__()
        self.view = view

    async def process_request(self, request: Request) -> Response:
        with self.request_context(request):
            return wrap_response(self.view(request))


def as_app(view: SingleView, /) -> SingleViewApp:
    """
    Decorator for using a single function as an app.
    """
    return SingleViewApp(view)


class App(BaseApp):
    """
    An application containing an automatic routing mechanism
    and error handling.
    """

    def __init__(self, *, router: Router | None = None) -> None:
        super().__init__()
        self.router = router or Router()

    async def _execute_view(self, view: RouteView) -> ResponseLike:
        logger.debug(f"Executing view: {view}")
        try:
            result = view()
            if isinstance(result, Awaitable):
                result = await result

            return result
        except HTTPError as error:
            logger.info(f"HTTP Error {error.status_code}")
            http_error = type(error)
            view = self.router.lookup_error(http_error)
            return await self._execute_view(view)
        except BaseException as exception:
            logger.exception(exception)
            view = self.router.lookup_error(InternalServerError)
            return await self._execute_view(view)

    async def process_request(self, request: Request) -> Response:
        logger.info(f"{request.method} {request.path}")
        route: Route | None = self.router.lookup_route(request.path)
        view: RouteView
        if route is None:
            view = self.router.lookup_error(NotFound)
        else:
            view = route.view

        with self.request_context(request):
            response = await self._execute_view(view)

        return wrap_response(response)

    def route(self, path: str, /, *, method: Method) -> RouteDecorator:
        """
        Decorator interface for adding a route to the app.
        """

        def decorator(view: RouteViewVar, /) -> RouteViewVar:
            self.router.push_route(view, path, method)
            return view

        return decorator

    def get(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a GET route.
        """
        return self.route(path, method=Method.GET)

    def post(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a POST route.
        """
        return self.route(path, method=Method.POST)

    def put(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a PUT route.
        """
        return self.route(path, method=Method.PUT)

    def patch(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a PATCH route.
        """
        return self.route(path, method=Method.PATCH)

    def delete(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a DELETE route.
        """
        return self.route(path, method=Method.DELETE)

    def connect(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a CONNECT route.
        """
        return self.route(path, method=Method.CONNECT)

    def options(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding an OPTIONS route.
        """
        return self.route(path, method=Method.OPTIONS)

    def trace(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a TRACE route.
        """
        return self.route(path, method=Method.TRACE)

    def head(self, path: str, /) -> RouteDecorator:
        """
        Decorator interface for adding a HEAD route.
        """
        return self.route(path, method=Method.HEAD)

    def error(self, status: int | type[HTTPError], /) -> RouteDecorator:
        """
        Decorator interface for adding an error handler to the app.
        """

        def decorator(view: RouteViewVar, /) -> RouteViewVar:
            self.router.push_error(status, view)
            return view

        return decorator
