from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import ClassVar, Final, Self, TYPE_CHECKING
import time
import asyncio
from datetime import datetime
import calendar

if TYPE_CHECKING:
    from collections.abc import Sequence, Mapping


@dataclass(slots=True, frozen=True)
class LogLevel:
    """
    An arbitrary log level.
    """

    name: str
    level: int

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, LogLevel):
            return NotImplemented

        return self.level > other.level

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LogLevel):
            return NotImplemented

        return self.level < other.level


DEBUG: Final[LogLevel] = LogLevel("debug", 0)
INFO: Final[LogLevel] = LogLevel("info", 100)
WARNING: Final[LogLevel] = LogLevel("info", 1000)
CRITICAL: Final[LogLevel] = LogLevel("critical", 10_000)


@dataclass(slots=True)
class Message:
    level: LogLevel
    objects: Sequence[object]
    named_objects: Mapping[str, object]
    timestamp: float = field(default_factory=time.time)

    def as_string(self) -> str:
        objects_list = [str(item) for item in self.objects]
        for name, value in self.named_objects.items():
            objects_list.append(f"{name}={value}")

        message = " ".join(objects_list)
        return message


@dataclass(slots=True)
class Logger:
    """
    An independent logger for the current context.
    """

    current_logger: ClassVar[ContextVar[Logger]] = ContextVar("current_logger")

    current_level: LogLevel = INFO
    quiet: bool = field(default=False, init=False)
    reset_token: Token[Logger] | None = field(
        default=None, repr=False, init=False
    )

    # TODO: Factor this out into its own class
    write_task: asyncio.Task[None] | None = field(
        default=None, repr=False, init=False
    )
    write_queue: asyncio.Queue[Message] = field(
        default_factory=asyncio.Queue, repr=False, init=False
    )
    writer_done: bool = field(default=False, repr=False, init=False)

    def shut_up(self) -> None:
        self.quiet = True

    async def _writer(self) -> None:
        while not self.writer_done:
            message = await self.write_queue.get()
            when = datetime.fromtimestamp(message.timestamp)
            month = calendar.month_abbr[when.month]
            # TODO: Add a dedicated file stream
            print(
                f"{month} {when.day}, {when.hour}:{when.minute}:{when.second} [{message.level.name}] {message.as_string()}"
            )
            self.write_queue.task_done()

    def dispatch_message(self, message: Message) -> None:
        """
        Output a log message with an arbitrary log level.
        """
        if self.quiet or (message.level > self.current_level):
            return

        self.write_queue.put_nowait(message)

    def debug(self, *objects: object, **named_objects: object) -> None:
        """
        Output a debug message.
        """
        self.dispatch_message(Message(DEBUG, objects, named_objects))

    def info(self, *objects: object, **named_objects: object) -> None:
        """
        Output an informative message.
        """
        self.dispatch_message(Message(INFO, objects, named_objects))

    def warning(self, *objects: object, **named_objects: object) -> None:
        """
        Output an "unfixable" warning (a warning that wasn't the fault of the
        user).
        """
        self.dispatch_message(Message(WARNING, objects, named_objects))

    def critical(self, *objects: object, **named_objects: object) -> None:
        """
        Output a critical message.
        """
        self.dispatch_message(Message(CRITICAL, objects, named_objects))

    @classmethod
    def current(cls) -> Logger:
        """
        Get the logger for the current context. This raises an exception if
        no logger is set.
        """
        return cls.current_logger.get()

    async def __aenter__(self) -> Self:
        self.reset_token = self.current_logger.set(self)
        assert self.write_task is None
        self.write_task = asyncio.create_task(self._writer())
        return self

    async def __aexit__(self, *_: object) -> None:
        assert self.reset_token is not None
        assert self.write_task is not None
        await self.write_queue.join()
        self.writer_done = True
        self.current_logger.reset(self.reset_token)
