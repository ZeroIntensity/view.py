"""
General utilities for view.py users.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
from typing import ClassVar, Self, Any
from contextvars import ContextVar, Token

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


@dataclass(slots=True)
class StartStopMixin(ABC):
    _wakeup_event: asyncio.Event = field(
        default_factory=asyncio.Event, init=False, repr=False
    )
    _start_task: asyncio.Task[None] | None = field(
        default=None, init=False, repr=False
    )
    _current_token: Token[Self | None] | None = field(
        default=None, init=False, repr=False
    )

    _current: ClassVar[ContextVar["Self | None"]] = ContextVar(
        "_current", default=None
    )

    @property
    def running(self) -> bool:
        return self._wakeup_event.is_set()

    @abstractmethod
    async def start(self) -> None: ...

    def stop(self) -> None:
        if self.running is False:
            raise RuntimeError(f"{self} is not running")

        self._wakeup_event.clear()

    async def __aenter__(self) -> Self:
        if self.running:
            raise RuntimeError(f"{self} is already running")

        self._current_token = self._current.set(self)
        self._start_task = asyncio.create_task(self.start())
        await self._wakeup_event.wait()
        return self

    async def __aexit__(self, *_: Any) -> None:
        try:
            self.stop()
            assert self._start_task is not None
            await self._start_task
        finally:
            assert self._current_token is not None
            self._current.reset(self._current_token)
            self._current_token = None

    @classmethod
    def current(cls) -> Self:
        manager = cls._current.get()
        if manager is None:
            raise RuntimeError(
                f"no instance of {cls.__name__} is currently available"
            )

        return manager
