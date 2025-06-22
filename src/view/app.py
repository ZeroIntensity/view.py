from view.router import Router
from dataclasses import dataclass
from multidict import CIMultiDict

__all__ = "App", "new_app"

@dataclass(slots=True, frozen=True)
class Request:
    path: str
    headers: CIMultiDict

class App(Router):
    def process_request(self, request: Request):
        pass

def new_app() -> App:
    """
    High-level function for constructing a view.py application.
    """
    ...
