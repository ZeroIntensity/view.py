"""
Rich logging and asynchronous log management.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator, Iterable
from contextlib import AsyncExitStack, asynccontextmanager, suppress
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from datetime import datetime as DateTime
from typing import AsyncContextManager, ClassVar, TypeAlias, TypeVar

from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.text import Text
from rich.traceback import Traceback
from typing_extensions import Self

from view.__about__ import __version__

__all__ = ("LogRecord", "LogLevels", "LogLevel", "LogManager", "Logger")

_STARTUP_BANNER = r"""        _
 _   __(_)__ _      __  ____  __  __
| | / / / _ \ | /| / / / __ \/ / / /
| |/ / /  __/ |/ |/ / / /_/ / /_/ /
|___/_/\___/|__/|__(_) .___/\__, /
                    /_/    /____/"""

LogMessage: TypeAlias = str | RenderableType
T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class LogLevel:
    name: str
    color: str
    priority: int


class LogLevels:
    DEBUG = LogLevel("debug", "dark_green", 0)
    INFO = LogLevel("info", "cyan", 1)
    WARNING = LogLevel("warning", "bright_yellow", 2)
    ERROR = LogLevel("error", "bright_red", 3)
    CRITICAL = LogLevel("critical", "red", 4)


@dataclass(frozen=True, slots=True)
class LogRecord:
    origin: Logger
    level: LogLevel
    message: Iterable[LogMessage]
    created: float
    show_prefix: bool = True


@dataclass(slots=True)
class LogManager:
    """
    Print logs immediately, or queue them inside an async context manager.
    """

    level: LogLevel = field(default=LogLevels.INFO)
    console: Console = field(default_factory=Console)
    _queue: asyncio.Queue[LogRecord] = field(
        init=False, default_factory=asyncio.Queue, repr=False
    )
    _wakeup_event: asyncio.Event = field(
        init=False, default_factory=asyncio.Event, repr=False
    )
    _start_task: asyncio.Task[None] | None = field(
        init=False, default=None, repr=False
    )
    _current_token: Token[LogManager] | None = field(
        init=False, default=None, repr=False
    )
    _current: ClassVar[ContextVar[LogManager]] = ContextVar(
        "current_log_manager"
    )

    @property
    def running(self) -> bool:
        return self._wakeup_event.is_set()

    def log(
        self,
        logger: Logger,
        level: LogLevel,
        *message: LogMessage,
        show_prefix: bool = True,
    ) -> None:
        if logger.disabled or self.level.priority > level.priority:
            return

        record = LogRecord(
            origin=logger,
            level=level,
            message=message,
            created=time.time(),
            show_prefix=show_prefix,
        )
        # App construction, WSGI and test clients do not require a log worker.
        if self.running:
            self._queue.put_nowait(record)
        else:
            self._handle_record(record)

    def _handle_record(self, record: LogRecord, /) -> None:
        with self.console:
            if record.show_prefix:
                date = DateTime.fromtimestamp(record.created)
                formatted = date.strftime("%d %B %H:%M:%S.%f")
                level = record.level
                level_name = f" {level.name} "

                time_align = " " * (15 - len(record.origin.name))
                message_align = " " * (10 - len(level_name))

                self.console.print(
                    f"\\[[bold light_sea_green]{record.origin.name}[/]]"
                    f"{time_align}\\[[bright_black]{formatted}[/]] "
                    f"{message_align}[bold white on {level.color}]"
                    f"{level_name}[/] ",
                    highlight=False,
                    end="",
                )
            self.console.print(*record.message)

    async def _drain(self) -> None:
        while not self._queue.empty():
            record = await self._queue.get()
            await asyncio.to_thread(self._handle_record, record)

    async def start(self) -> None:
        if self.running:
            raise RuntimeError("log manager is already running")

        self._wakeup_event.set()
        try:
            while self.running:
                await self._drain()
                await asyncio.sleep(0.01)
        finally:
            self._wakeup_event.clear()
            await self._drain()

    def stop(self) -> None:
        if not self.running:
            raise RuntimeError("log manager is not running")

        self._wakeup_event.clear()

    async def __aenter__(self) -> Self:
        if self.running:
            raise RuntimeError("log manager is already running")

        self._current_token = self._current.set(self)
        self._start_task = asyncio.create_task(self.start())
        await self._wakeup_event.wait()
        return self

    async def __aexit__(self, *_: object) -> None:
        try:
            if self.running:
                self.stop()
            assert self._start_task is not None
            await self._start_task
        finally:
            assert self._current_token is not None
            self._current.reset(self._current_token)
            self._current_token = None
            self._start_task = None

    @classmethod
    def current(cls) -> LogManager:
        try:
            return cls._current.get()
        except LookupError:
            raise RuntimeError(
                "no log manager is currently available"
            ) from None

    def print_startup_message(self) -> None:
        self.console.print(
            Panel.fit(
                Text(_STARTUP_BANNER, style="bold cyan", justify="left"),
                border_style="cyan",
                padding=(1, 2),
                title=Text(f"v{__version__}", style="bold white"),
            )
        )

    def create_logger(self, name: str) -> Logger:
        return Logger(self, name, level=self.level)


@dataclass(slots=True)
class Logger:
    manager: LogManager
    name: str
    level: LogLevel = field(default=LogLevels.INFO)
    disabled: bool = False

    def _is_enabled_for(self, level: LogLevel) -> bool:
        return (
            not self.disabled
            and self.level.priority <= level.priority
            and self.manager.level.priority <= level.priority
        )

    def log(
        self, level: LogLevel, *message: LogMessage, show_prefix: bool = True
    ) -> None:
        if not self._is_enabled_for(level):
            return

        self.manager.log(self, level, *message, show_prefix=show_prefix)

    def debug(self, *message: LogMessage) -> None:
        self.log(LogLevels.DEBUG, *message)

    def info(self, *message: LogMessage) -> None:
        self.log(LogLevels.INFO, *message)

    def warning(self, *message: LogMessage) -> None:
        self.log(LogLevels.WARNING, *message)

    def error(self, *message: LogMessage) -> None:
        self.log(LogLevels.ERROR, *message)

    def critical(self, *message: LogMessage) -> None:
        self.log(LogLevels.CRITICAL, *message)

    def exception(self, *message: LogMessage) -> None:
        if not self._is_enabled_for(LogLevels.CRITICAL):
            return

        self.log(LogLevels.CRITICAL, *message)
        self.log(LogLevels.CRITICAL, Traceback(), show_prefix=False)

    @asynccontextmanager
    async def log_time(
        self,
        what: str,
        /,
        *,
        warning_time: float = 3,
        level: LogLevel = LogLevels.DEBUG,
    ) -> AsyncGenerator[None, None]:
        if not self._is_enabled_for(level):
            yield
            return

        first = time.perf_counter()

        async def _warning_task() -> None:
            await asyncio.sleep(warning_time)
            self.warning(
                f"{what} is slow; taken at least {warning_time} seconds"
            )

        task = asyncio.create_task(_warning_task())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

            elapsed_ms = (time.perf_counter() - first) * 1000
            self.log(level, f"{what} took {round(elapsed_ms, 6)}ms")

    @asynccontextmanager
    async def wrap_log_time(
        self,
        what: str,
        ctx: AsyncContextManager[T],
        /,
        *,
        warning_time: float = 3,
        level: LogLevel = LogLevels.DEBUG,
    ) -> AsyncGenerator[T, None]:
        async with AsyncExitStack() as stack:
            async with self.log_time(
                what, warning_time=warning_time, level=level
            ):
                result = await stack.enter_async_context(ctx)
            yield result
