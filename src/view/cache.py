from __future__ import annotations
from typing import ParamSpec, TypeVar, Callable, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time
import math

from multidict import CIMultiDict

from view.response import Response, StrOrBytesResponse, ViewResult, wrap_view_result

__all__ = ("in_memory_cache",)

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
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response: ...


@dataclass(slots=True, frozen=True)
class CachedResponse:
    body: bytes
    headers: CIMultiDict[str]
    status: int
    last_reset: float

    @classmethod
    async def from_response(cls, response: Response) -> CachedResponse:
        body = await response.body()
        return cls(body, response.headers, response.status_code, time.time())

    def as_response(self) -> Response:
        return StrOrBytesResponse.from_content(
            self.body, status_code=self.status, headers=self.headers
        )


@dataclass(slots=True)
class InMemoryCache(BaseCache[P, T]):
    """
    Wrapper class for a cache stored in memory.
    """

    callable: Callable[P, T]
    reset_frequency: float
    cached_response: CachedResponse | None = field(repr=False, default=None)

    def invalidate(self) -> None:
        self.cached_response = None

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        if self.cached_response is None:
            result = await wrap_view_result(self.callable(*args, **kwargs))
            cached = await CachedResponse.from_response(result)
            self.cached_response = cached
            return cached.as_response()

        if (time.time() - self.cached_response.last_reset) > self.reset_frequency:
            self.invalidate()
            return await self(*args, **kwargs)

        return self.cached_response.as_response()


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
