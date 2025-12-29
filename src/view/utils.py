from contextlib import contextmanager
from functools import wraps
from typing import Callable, Iterator, ParamSpec, TypeVar

__all__ = "reraise", "reraises"


@contextmanager
def reraise(
    new_exception: type[BaseException] | BaseException, *exceptions: type[BaseException]
) -> Iterator[None]:
    """
    Context manager to reraise one or many exceptions as a single exception.

    This is primarily useful for reraising exceptions into HTTP errors, such
    as an error 400 (Bad Request).
    """
    try:
        yield
    except exceptions or Exception as error:
        raise new_exception from error


T = TypeVar("T")
P = ParamSpec("P")


def reraises(
    new_exception: type[BaseException] | BaseException, *exceptions: type[BaseException]
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to reraise one or many exceptions as a single exception for an
    entire function.

    This is primarily useful for reraising exceptions into HTTP errors, such
    as an error 400 (Bad Request).
    """

    def factory(function: Callable[P, T], /) -> Callable[P, T]:
        @wraps(function)
        def decorator(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return function(*args, **kwargs)
            except exceptions or Exception as error:
                raise new_exception from error

        return decorator

    return factory
