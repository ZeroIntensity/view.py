import functools
import inspect
import platform
import sys
from typing import Any, Callable

import pytest

ITERATIONS: int = 100


def pytest_addoption(parser: Any) -> None:
    parser.addoption("--enable-leak-tracking", action="store_true")


def limit_leaks(memstring: str):
    def decorator(func: Callable):
        if "--enable-leak-tracking" not in sys.argv:
            return func

        if platform.system() != "Windows":
            if not inspect.iscoroutinefunction(func):

                @functools.wraps(func)
                def wrapper(*args, **kwargs):  # type: ignore
                    for _ in range(ITERATIONS):
                        func(*args, **kwargs)

            else:

                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    for _ in range(ITERATIONS):
                        await func(*args, **kwargs)

                wrapper = pytest.mark.asyncio(wrapper)

            return pytest.mark.limit_leaks(memstring)(wrapper)
        else:
            return func

    return decorator
