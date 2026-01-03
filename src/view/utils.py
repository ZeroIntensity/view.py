from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = ("reraise",)


@contextmanager
def reraise(
    new_exception: type[BaseException] | BaseException,
    *exceptions: type[BaseException],
) -> Iterator[None]:
    """
    Context manager to reraise one or many exceptions as a single exception.

    This is primarily useful for reraising exceptions into HTTP errors, such
    as an error 400 (Bad Request).
    """
    target = exceptions or Exception

    try:
        yield
    except target as error:
        raise new_exception from error
