from __future__ import annotations

import contextlib
import contextvars
import warnings
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Iterator
import multiprocessing
from pathlib import Path
from typing import TYPE_CHECKING, ParamSpec, TypeAlias, TypeVar

from loguru import logger

from view.core.request import Method, Request
from view.core.response import (
    FileResponse,
    Response,
    ResponseLike,
    ViewResult,
    wrap_view_result,
)
from view.core.router import FoundRoute, Route, Router, RouteView
from view.core.status_codes import Forbidden, HTTPError, InternalServerError, NotFound
from view.utils import reraise

if TYPE_CHECKING:
    from view.run.asgi import ASGIProtocol
    from view.run.wsgi import WSGIProtocol

__all__ = "BaseApp", "as_app", "App"

T = TypeVar("T")
P = ParamSpec("P")


class BaseApp(ABC):
    """Base view.py application."""

    _CURRENT_APP = contextvars.ContextVar["BaseApp"]("Current app being used.")

    def __init__(self):
        self._request = contextvars.ContextVar[Request](
            "The current request being handled."
        )
        self._production: bool | None = None

    @property
    def debug(self) -> bool:
        """
        Is the app in debug mode?

        If debug mode is enabled, some extra checks and settings are enabled
        to improve the development experience, at the cost of being slower and
        less secure.
        """
        if self._production is None:
            return __debug__

        return self._production

    @contextlib.contextmanager
    def request_context(self, request: Request) -> Iterator[None]:
        """
        Enter a context for the given request.
        """
        with logger.contextualize(request=request):
            app_token = self._CURRENT_APP.set(self)
            request_token = self._request.set(request)
            try:
                yield
            finally:
                self._request.reset(request_token)
                self._CURRENT_APP.reset(app_token)

    @classmethod
    def current_app(cls) -> BaseApp:
        return cls._CURRENT_APP.get()

    def current_request(self) -> Request:
        """
        Get the current request being handled.
        """
        return self._request.get()

    @abstractmethod
    async def process_request(self, request: Request) -> Response:
        """
        Get the response from the server for a given request.
        """

    def wsgi(self) -> WSGIProtocol:
        """
        Get the WSGI callable for the app.
        """
        from view.run.wsgi import wsgi_for_app

        return wsgi_for_app(self)

    def asgi(self) -> ASGIProtocol:
        """
        Get the ASGI callable for the app.
        """
        from view.run.asgi import asgi_for_app

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
        from view.run.servers import ServerSettings

        # If production is True, then __debug__ should be False.
        # If production is False, then __debug__ should be True.
        if production is __debug__:
            warnings.warn(
                f"The app was run with {production=}, but Python's {__debug__=}",
                RuntimeWarning,
            )

        logger.info(f"Serving app on http://localhost:{port}")
        self._production = production
        settings = ServerSettings(self, host=host, port=port, hint=server_hint)
        try:
            settings.run_app_on_any_server()
        except KeyboardInterrupt:
            logger.info("CTRL^C received, shutting down")
        except Exception:
            logger.exception("Error in server lifecycle")
        finally:
            logger.info("Server finished")

    def run_detached(
        self,
        *,
        host: str = "localhost",
        port: int = 5000,
        production: bool = False,
        server_hint: str | None = None,
    ) -> multiprocessing.Process:
        """
        Run the app in a separate process. This means that the server is
        killable.
        """

        context = multiprocessing.get_context("fork")
        process = context.Process(
            target=self.run,
            kwargs={
                "host": host,
                "port": port,
                "production": production,
                "server_hint": server_hint,
            },
        )
        process.start()
        return process


async def _execute_view_internal(
    view: Callable[P, ViewResult],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Response:
    logger.debug(f"Executing view: {view}")
    try:
        result = view(*args, **kwargs)
        return await wrap_view_result(result)
    except HTTPError as error:
        logger.opt(colors=True).info(f"<red>HTTP Error {error.status_code}</red>")
        raise


async def execute_view(
    view: Callable[P, ViewResult], *args: P.args, **kwargs: P.kwargs
) -> Response:
    try:
        return await _execute_view_internal(view, *args, **kwargs)
    except BaseException as exception:
        # Let HTTP errors pass through, so the caller can deal with it
        if isinstance(exception, HTTPError):
            raise
        logger.exception(exception)
        if __debug__:
            raise InternalServerError.from_current_exception()
        else:
            raise InternalServerError()


SingleView = Callable[["Request"], ViewResult]


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
                return await execute_view(self.view, request)
            except HTTPError as error:
                return error.as_response()


def as_app(view: SingleView, /) -> SingleViewApp:
    """
    Decorator for using a single function as an app.
    """
    if __debug__ and not callable(view):
        raise InvalidType(view, Callable)

    return SingleViewApp(view)


RouteDecorator: TypeAlias = Callable[[RouteView], Route]
SubRouterView: TypeAlias = Callable[[str], ResponseLike | Awaitable[ResponseLike]]
SubRouterViewT = TypeVar("SubRouterViewT", bound=SubRouterView)


class App(BaseApp):
    """
    An application containing an automatic routing mechanism
    and error handling.
    """

    def __init__(self, *, router: Router | None = None) -> None:
        super().__init__()
        self.router = router or Router()

    async def _process_request_internal(self, request: Request) -> Response:
        logger.opt(colors=True).info(
            f"<yellow>{request.method}</yellow> <green>{request.path}</green>"
        )
        found_route: FoundRoute | None = self.router.lookup_route(
            request.path, request.method
        )
        if found_route is None:
            raise NotFound()

        # Extend instead of replacing?
        request.path_parameters = found_route.path_parameters
        return await execute_view(found_route.route.view)

    async def process_request(self, request: Request) -> Response:
        with self.request_context(request):
            try:
                return await self._process_request_internal(request)
            except HTTPError as error:
                error_view = self.router.lookup_error(type(error))
                if error_view is not None:
                    return await execute_view(error_view)

                return error.as_response()

    def route(self, path: str, /, *, method: Method) -> RouteDecorator:
        """
        Decorator interface for adding a route to the app.
        """

        if __debug__ and not isinstance(path, str):
            raise InvalidType(path, str)

        if __debug__ and not isinstance(method, Method):
            raise InvalidType(method, Method)

        def decorator(view: RouteView, /) -> Route:
            route = self.router.push_route(view, path, method)
            return route

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

    def error(
        self, status: int | type[HTTPError], /
    ) -> Callable[[RouteView], RouteView]:
        """
        Decorator interface for adding an error handler to the app.
        """

        def decorator(view: RouteView, /) -> RouteView:
            self.router.push_error(status, view)
            return view

        return decorator

    def subrouter(self, path: str) -> Callable[[SubRouterViewT], SubRouterViewT]:
        if __debug__ and not isinstance(path, str):
            raise InvalidType(path, str)

        def decorator(function: SubRouterViewT, /) -> SubRouterViewT:
            if __debug__ and not callable(function):
                raise InvalidType(Callable, function)

            def router_function(path_from_url: str) -> Route:
                def route() -> ResponseLike | Awaitable[ResponseLike]:
                    return function(path_from_url)

                return Route(route, path_from_url, Method.GET)

            self.router.push_subrouter(router_function, path)
            return function

        return decorator

    def static_files(self, path: str, directory: str | Path) -> None:
        if __debug__ and not isinstance(directory, (str, Path)):
            raise InvalidType(directory, str, Path)

        directory = Path(directory)

        @self.subrouter(path)
        def serve_static_file(path_from_url: str) -> ResponseLike:
            file = directory / path_from_url
            if not file.is_file():
                raise NotFound()

            if not file.is_relative_to(directory):
                raise Forbidden()

            with reraise(Forbidden, OSError):
                return FileResponse.from_file(file)
