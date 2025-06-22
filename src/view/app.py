from view.router import Route, Router, Response
from dataclasses import dataclass
from multidict import CIMultiDict

__all__ = "App", "new_app"


@dataclass(slots=True, frozen=True)
class Request:
    path: str
    headers: CIMultiDict

class App(Router):
    def process_request(self, request: Request) -> Response:
        route: Route | None = self.lookup_route(request.path)
        if route is None:
            ...
        return NotImplemented


def new_app() -> App:
    """
    High-level function for constructing a view.py application.
    """
    ...
