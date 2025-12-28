from __future__ import annotations

import sys
from typing import Any, ClassVar

__all__ = "ViewError", "explain"


def _base_help(code: int) -> str:
    return f"Unsure what to do? Run `view explain {code}`"


CODES: dict[int, type[ViewError]] = {}
_NEXT_GLOBAL_CODE: int = 1000


class ViewError(Exception):
    """
    Base class for all exceptions in view.py
    """

    code: ClassVar[int] = -1

    def __init_subclass__(cls) -> None:
        global _NEXT_GLOBAL_CODE, __all__
        cls.code = _NEXT_GLOBAL_CODE
        _NEXT_GLOBAL_CODE += 1

        __all__ += (cls.__name__,)

    def __init__(self, *msg: str) -> None:
        self.message = " ".join(msg)
        super().__init__(
            f"[Error code {self.code}]: {self.message}" f"{_base_help(self.code)}"
        )


class InvalidType(ViewError, TypeError):
    """
    Something got a type that it didn't expect. For example, passing a
    `str` object in a place where a `bytes` object was expected would raise
    this error.

    In order to fix this, please review the documentation of the function
    you're attempting to call and ensure that you are passing it the correct
    types. view.py is completely type-safe, so if your editor/IDE is
    complaining about something, it is very likely the culprit.
    """

    def __init__(self, expected: type | tuple[type, ...], got: Any) -> None:
        if isinstance(expected, type):
            super().__init__(f"Expected {expected.__name__}, got {got!r}")
        else:
            expected_string = ", ".join([exception.__name__ for exception in expected])
            super().__init__(f"Expected {expected_string}, got {got!r}")


def explain(code: int) -> str:
    """
    Get the explanation for a given error code.
    """
    error_cls = CODES.get(code)
    if error_cls is None:
        raise RuntimeError(f"Unknown error code: {code}")

    if sys.flags.optimize >= 2:
        raise RuntimeError("Cannot explain errors when -OO is passed to Python")

    assert error_cls.__doc__ is not None, "Error class should have a docstring"
    return error_cls.__doc__
