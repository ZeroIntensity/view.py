from __future__ import annotations
from enum import Enum, auto
from typing import Awaitable, Callable, TypeAlias
from dataclasses import dataclass

__all__ = "Method", "Route", "Router"

class Method(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    PATCH = auto()
    DELETE = auto()
    CONNECT = auto()
    OPTIONS = auto()
    TRACE = auto()
    HEAD = auto()

RouteHandler: TypeAlias = Callable[[], None | Awaitable[None]]


@dataclass(slots=True, frozen=True)
class Route:
    handler: RouteHandler
    path: str
    method: Method


class Router:
    def __init__(self) -> None:
        self.routes: dict[str, Route] = {}

    def push_route(self, handler: RouteHandler, path: str, method: Method) -> None:
        self.routes[path] = Route(handler=handler, path=path, method=method)

    def route(self, path: str, /, *, method: Method):
        """
        Decorator interface for adding a route to the app.
        """
        def decorator(function: RouteHandler, /):
            self.push_route(function, path, method)
            return function
        return decorator

    def get(self, path: str, /):
        return self.route(path, method=Method.GET)
    
    def post(self, path: str, /):
        return self.route(path, method=Method.POST)
    
    def put(self, path: str, /):
        return self.route(path, method=Method.PUT)
    
    def patch(self, path: str, /):
        return self.route(path, method=Method.PATCH)
    
    def delete(self, path: str, /):
        return self.route(path, method=Method.DELETE)
    
    def connect(self, path: str, /):
        return self.route(path, method=Method.CONNECT)
    
    def options(self, path: str, /):
        return self.route(path, method=Method.OPTIONS)
    
    def trace(self, path: str, /):
        return self.route(path, method=Method.TRACE)
    
    def head(self, path: str, /):
        return self.route(path, method=Method.HEAD)
