from __future__ import annotations

import inspect
import sys
from datetime import datetime as DateTime
from pathlib import Path
from types import FrameType as Frame
from typing import Literal, TextIO

from rich.console import Console
from rich.markup import escape

__all__ = ("log",)

Urgency = Literal["debug", "info", "warn", "error"]
FileWriteMethod = Literal["only", "never", "both"]

_CurrentFrame = None
_Now = None
_StandardOut = None
_NoFile = None

_URGENCY_COLORS: dict[Urgency, str] = {
    "debug": "blue",
    "info": "green",
    "warn": "dim yellow",
    "error": "red",
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
    time_msg = (
        f"[bold dim blue]{time.strftime(strftime)}[/] " if show_time else ""
    )
    caller_msg = (
        f"[bold magenta]{f.f_back.f_code.co_filename}:{f.f_back.f_lineno}[/] "
        if show_caller
        else ""
    )
    urgency_msg = (
        f"[bold {_URGENCY_COLORS[urgency]}]{urgency}[/]: "
        if show_urgency
        else ""
    )
    msg = (
        time_msg
        + caller_msg
        + urgency_msg
        + " ".join([str(i) for i in messages])
    )

    if file_write != "only":
        Console(file=file_out or sys.stdout).print(
            msg,
            markup=show_color,
            highlight=show_color,
        )

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
