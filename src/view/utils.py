"""
General utilities for view.py users.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from contextlib import contextmanager

__all__ = ("reraise",)


@contextmanager
def reraise(
    new_exception: type[BaseException] | BaseException,
    *exceptions: type[BaseException],
) -> Generator[None]:
    """
    Context manager to reraise one or many exceptions as a single exception.

    This is primarily useful for reraising exceptions into HTTP errors, such
    as a :class:`~view.core.status_codes.BadRequest`.
    """
    target = exceptions or Exception

    try:
        yield
    except target as error:
        raise new_exception from error
