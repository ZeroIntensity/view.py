from __future__ import annotations

from typing import Any

__all__ = ("ViewError",)


class ViewError(Exception):
    """
    Base class for all exceptions in view.py
    """

    def __init__(self, *msg: str) -> None:
        super().__init__(*msg)


class InvalidTypeError(ViewError, TypeError):
    """
    Something got a type that it didn't expect. For example, passing a
    `str` object in a place where a `bytes` object was expected would raise
    this error.

    In order to fix this, please review the documentation of the function
    you're attempting to call and ensure that you are passing it the correct
    types. view.py is completely type-safe, so if your editor/IDE is
    complaining about something, it is very likely the culprit.
    """

    def __init__(self, got: Any, *expected: type) -> None:
        expected_string = ", ".join([exception.__name__ for exception in expected])
        super().__init__(f"Expected {expected_string}, but got {got!r}")
