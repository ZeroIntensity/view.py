from .response import HTML

__all__ = ("default_page",)


def default_page() -> HTML:
    """Return the view.py default page."""
    return HTML("")
