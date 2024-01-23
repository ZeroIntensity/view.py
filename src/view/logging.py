from __future__ import annotations

import inspect
import sys
from datetime import datetime as DateTime
from pathlib import Path
from types import FrameType as Frame
from typing import TextIO, TypedDict

from rich.console import Console
from typing_extensions import NotRequired, Unpack

from ._logging import _QUEUE, QueueItem
from .typing import FileWriteMethod
from .typing import LogLevel as Urgency

__all__ = (
    "log",
    "Urgency",
    "log",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
)

_CurrentFrame = None
_Now = None
_StandardOut = None
_NoFile = None

_URGENCY_COLORS: dict[str, str] = {
    "debug": "blue",
    "info": "green",
    "warning": "dim yellow",
    "error": "red",
    "critical": "dim red",
}


def log(
    *messages: object,
    urgency: Urgency = "info",
    file_out: TextIO | None = _StandardOut,
    log_file: Path | str | TextIO | None = _NoFile,
    caller_frame: Frame | None = _CurrentFrame,
    time: DateTime | None = _Now,
    show_time: bool = True,
    show_caller: bool = True,
    show_color: bool = True,
    show_urgency: bool = True,
    file_write: FileWriteMethod = "both",
    strftime: str = "%H:%M:%S",
) -> None:
    f = caller_frame or inspect.currentframe()
    assert f is not None
    assert f.f_back is not None
    time = time or DateTime.now()
    time_msg = f"[bold dim blue]{time.strftime(strftime)}[/] " if show_time else ""
    caller_msg = (
        f"[bold magenta]{f.f_back.f_code.co_filename}:{f.f_back.f_lineno}[/] "
        if show_caller
        else ""
    )
    urgency_msg = (
        f"[bold {_URGENCY_COLORS[urgency]}]{urgency}[/]: " if show_urgency else ""
    )
    msg = time_msg + caller_msg + urgency_msg + " ".join([str(i) for i in messages])

    if file_write != "only":
        Console(file=file_out or sys.stdout).print(
            msg,
            markup=show_color,
            highlight=show_color,
        )
        _QUEUE.put_nowait(QueueItem(True, False, urgency, msg + "\n", is_stdout=True))

    if (file_write != "never") and log_file:
        if isinstance(log_file, (str, Path)):
            log_path = Path(log_file)

            if log_path.exists():
                log_f = open(log_path, "a")
            else:
                log_f = open(log_path, "w")
        else:
            log_f = log_file

        Console(file=log_f).print(
            msg,
            markup=show_color,
            highlight=show_color,
        )


class _LogArgs(TypedDict):
    file_out: NotRequired[TextIO]
    log_file: NotRequired[Path | str | TextIO]
    caller_frame: NotRequired[Frame]
    time: NotRequired[DateTime]
    show_time: NotRequired[bool]
    show_caller: NotRequired[bool]
    show_color: NotRequired[bool]
    show_urgency: NotRequired[bool]
    file_write: NotRequired[FileWriteMethod]
    strftime: NotRequired[str]


def _get_last_frame() -> Frame:
    f = inspect.currentframe()
    assert f, "failed to get frame"
    assert f.f_back, "failed to get f_back"
    assert f.f_back.f_back, "f_back has no previous frame"
    return f.f_back.f_back


def _splat_args(args: _LogArgs) -> _LogArgs:
    if "caller_frame" not in args:
        args["caller_frame"] = _get_last_frame()

    return args


def debug(*messages: object, **kwargs: Unpack[_LogArgs]) -> None:
    log(*messages, urgency="debug", **_splat_args(kwargs))


def info(*messages: object, **kwargs: Unpack[_LogArgs]) -> None:
    log(*messages, urgency="info", **_splat_args(kwargs))


def warning(*messages: object, **kwargs: Unpack[_LogArgs]) -> None:
    log(*messages, urgency="warning", **_splat_args(kwargs))


def error(*messages: object, **kwargs: Unpack[_LogArgs]) -> None:
    log(*messages, urgency="error", **_splat_args(kwargs))


def critical(*messages: object, **kwargs: Unpack[_LogArgs]) -> None:
    log(*messages, urgency="critical", **_splat_args(kwargs))
