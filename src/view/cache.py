from __future__ import annotations
from typing import ParamSpec, TypeVar, Callable, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time
import math

from view.response import Response, ViewResult, wrap_view_result

__all__ = "in_memory_cache",

T = TypeVar("T", bound=ViewResult)
P = ParamSpec("P")

@dataclass(slots=True)
class BaseCache(ABC, Generic[P, T]):
    """
    Base class for caches.
    """
    callable: Callable[P, T]

    @abstractmethod
    def invalidate(self) -> None:
        """
        Invalidate the cache.
        """

    @abstractmethod
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        ...


@dataclass(slots=True)
class InMemoryCache(BaseCache[P, T]):
    """
    Wrapper class for a cache stored in memory.
    """
    callable: Callable[P, T]
    reset_frequency: float
    last_reset: float | None = None
    last_result: Response | None = field(repr=False, default=None)

    def invalidate(self) -> None:
        self.last_result = None
        self.last_reset = None

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        if self.last_result is None:
            new_result = await wrap_view_result(self.callable(*args, **kwargs))
            self.last_result = new_result
            self.last_reset = time.time()
            return new_result

        assert self.last_reset is not None
        if (time.time() - self.last_reset) > self.reset_frequency:
            self.invalidate()
            return await self(*args, **kwargs)

        return self.last_result


def minutes(number: int, /) -> int:
    return number * 60


def seconds(number: int, /) -> int:
    return number


def hours(number: int, /) -> int:
    return minutes(60) * number


def days(number: int, /) -> int:
    return hours(24) * number


def in_memory_cache(
    reset_frequency: int | None = None,
) -> Callable[[Callable[P, T]], InMemoryCache[P, T]]:
    def decorator_factory(function: Callable[P, T], /) -> InMemoryCache[P, T]:
        return InMemoryCache(function, reset_frequency=reset_frequency or math.inf)

    return decorator_factory
