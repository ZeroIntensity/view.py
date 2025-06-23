from __future__ import annotations

import contextlib
import contextvars
import warnings
from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import (TYPE_CHECKING, Callable, Iterator, Literal, ParamSpec,
                    TypeAlias, TypeVar, Union, overload)

from loguru import logger

from view.request import Method, Request
from view.response import Response, ResponseLike, wrap_response
from view.router import Route, Router, RouteView
from view.run import ServerSettings
from view.status_codes import HTTPError, InternalServerError, NotFound

if TYPE_CHECKING:
    from view.asgi import ASGIProtocol
    from view.wsgi import WSGIProtocol

__all__ = "BaseApp", "as_app", "App"

RouteViewVar = TypeVar("RouteViewVar", bound=RouteView)
RouteDecorator: TypeAlias = Callable[[RouteViewVar], RouteViewVar]


class BaseApp(ABC):
    """Base view.py application."""

    def __init__(self):
        self._request = contextvars.ContextVar[Request](
            "The current request being handled."
        )
        self._production: bool | None = None

    @property
    def debug(self) -> bool:
        if self._production is None:
            return __debug__

        return self._production

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
    def current_request(self, *, validate: Literal[False]) -> Request | None: ...

    @overload
    def current_request(self, *, validate: Literal[True] = True) -> Request: ...

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

    def wsgi(self) -> WSGIProtocol:
        """
        Get the WSGI callable for the app.
        """
        from view.wsgi import wsgi_for_app

        return wsgi_for_app(self)

    def asgi(self) -> ASGIProtocol:
        """
        Get the ASGI callable for the app.
        """
        from view.asgi import asgi_for_app

        return asgi_for_app(self)

    def run(
        self,
        *,
        host: str = "localhost",
        port: int = 5000,
        production: bool = False,
        server_hint: str | None = None,
    ) -> None:
        """
        Run the app.

        This is a sort of magic function that's supposed to "just work". If
        finer control over the server settings is desired, explicitly use the
        server's API with the app's `asgi` or `wsgi` method.
        """

        # production=True, __debug__ should be False.
        # production=False, __debug__ should be True.
        if production is __debug__:
            warnings.warn(
                f"The app was run with {production=}, but Python's {__debug__=}",
                RuntimeWarning,
            )

        self._production = production
        settings = ServerSettings(self, host=host, port=port, hint=server_hint)
        settings.run_app_on_any_server()


P = ParamSpec("P")


async def execute_view(
    view: Callable[P, ResponseLike | Awaitable[ResponseLike]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> ResponseLike:
    logger.debug(f"Executing view: {view}")
    try:
        result = view(*args, **kwargs)
        if isinstance(result, Awaitable):
            result = await result

        return result
    except HTTPError as error:
        logger.info(f"HTTP Error {error.status_code}")
        raise
    except BaseException as exception:
        logger.exception(exception)
        raise InternalServerError() from exception


SingleView = Callable[["Request"], Union["ResponseLike", Awaitable["ResponseLike"]]]


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
            try:
                response = await execute_view(self.view, request)
                return wrap_response(response)
            except HTTPError as error:
                return error.as_response()


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

    async def _process_request_internal(self, request: Request) -> Response:
        logger.info(f"{request.method} {request.path}")
        route: Route | None = self.router.lookup_route(request.path)
        if route is None:
            raise NotFound()

        response = await execute_view(route.view)
        return wrap_response(response)

    async def process_request(self, request: Request) -> Response:
        with self.request_context(request):
            try:
                return await self._process_request_internal(request)
            except HTTPError as error:
                error_view = self.router.lookup_error(type(error))
                if error_view is not None:
                    return wrap_response(await execute_view(error_view))

                return error.as_response()

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
