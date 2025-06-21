from view.router import Router

__all__ = "App", "new_app"


class App(Router):
    def process_request(self):
        pass

def new_app() -> App:
    """
    High-level function for constructing a view.py application.
    """
    ...
