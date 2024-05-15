import platform
from typing import Callable
import pytest

def limit_leaks(memstring: str):
    def decorator(func: Callable):
        if platform.system() != "Windows":
            func = pytest.mark.limit_leaks(memstring)(func)
            return func
        else:
            return func
    return decorator