from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import ClassVar, Final, Self


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
class Logger:
    """
    An independent logger for the current context.
    """

    current_logger: ClassVar[ContextVar[Logger]] = ContextVar("current_logger")

    current_level: LogLevel = field(default=INFO)
    reset_token: Token[Logger] | None = field(default=None)

    def shut_up(self) -> None:
        pass

    def message(
        self, level: LogLevel, *objects: object, **data: object
    ) -> None:
        """
        Output a log message with an arbitrary log level.
        """
        if level > self.current_level:
            return

        objects_list = [str(item) for item in objects]
        for name, value in data.items():
            objects_list.append(f"{name}={value}")

        message = " ".join(objects_list)
        print(f"{level.name}: {message}")

    def debug(self, *message: object, **data: object) -> None:
        """
        Output a debug message.
        """
        self.message(DEBUG, *message, **data)

    def info(self, *message: object, **data: object) -> None:
        """
        Output an informative message.
        """
        self.message(INFO, *message, **data)

    def warning(self, *message: object, **data: object) -> None:
        """
        Output an "unfixable" warning (a warning that wasn't the fault of the
        user).
        """
        self.message(WARNING, *message, **data)

    def critical(self, *message: object, **data: object) -> None:
        """
        Output a critical message.
        """
        self.message(CRITICAL, *message, **data)

    @classmethod
    def current(cls) -> Logger:
        """
        Get the logger for the current context. This raises an exception if
        no logger is set.
        """
        return cls.current_logger.get()

    def __enter__(self) -> Self:
        self.reset_token = self.current_logger.set(self)
        return self

    def __exit__(self, *_: object) -> None:
        assert self.reset_token is not None
        self.current_logger.reset(self.reset_token)
