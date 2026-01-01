from __future__ import annotations

import math
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generic, ParamSpec, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

from view.core.response import (
    Response,
    TextResponse,
    ViewResult,
    wrap_view_result,
)
from view.core.headers import RequestHeaders

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
    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response: ...


@dataclass(slots=True, frozen=True)
class _CachedResponse:
    body: bytes
    headers: RequestHeaders
    status: int
    last_reset: float

    @classmethod
    async def from_response(cls, response: Response) -> _CachedResponse:
        body = await response.body()
        return cls(body, response.headers, response.status_code, time.time())

    def as_response(self) -> Response:
        return TextResponse.from_content(
            self.body, status_code=self.status, headers=self.headers
        )


@dataclass(slots=True)
class InMemoryCache(BaseCache[P, T]):
    """
    Wrapper class for a cache stored in memory.
    """

    callable: Callable[P, T]
    reset_frequency: float
    _cached_response: _CachedResponse | None = field(repr=False, default=None)

    def invalidate(self) -> None:
        self._cached_response = None

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Response:
        if self._cached_response is None:
            result = await wrap_view_result(self.callable(*args, **kwargs))
            cached = await _CachedResponse.from_response(result)
            self._cached_response = cached
            return cached.as_response()

        if (
            time.time() - self._cached_response.last_reset
        ) > self.reset_frequency:
            self.invalidate()
            return await self(*args, **kwargs)

        return self._cached_response.as_response()


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
    """
    Decorator to cache the result from a given view in-memory.
    """

    def decorator_factory(function: Callable[P, T], /) -> InMemoryCache[P, T]:
        return InMemoryCache(
            function, reset_frequency=reset_frequency or math.inf
        )

    return decorator_factory
