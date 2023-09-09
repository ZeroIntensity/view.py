from __future__ import annotations

import getpass
import importlib
import inspect
import os
import pathlib
import socket
import warnings
import weakref
from collections.abc import Iterable
from types import FrameType as Frame
from types import FunctionType as Function
from types import ModuleType as Module
from typing import get_type_hints

from rich.panel import Panel
from rich.syntax import Syntax

from ._logging import Internal
from .exceptions import InvalidBodyError, MissingLibraryError, NotLoadedWarning
from .typing import Any, ViewBody, ViewBodyLike


class LoadChecker:
    _view_loaded: bool

    def _view_load_check(self) -> None:
        if (not self._view_loaded) and (
            not os.environ.get("_VIEW_CANCEL_FINALIZERS")
        ):
            warnings.warn(f"{self} was never loaded", NotLoadedWarning)

    def __post_init__(self) -> None:
        self._view_loaded = False
        weakref.finalize(self, self._view_load_check)


def set_load(cl: LoadChecker):
    """Let the developer feel that they aren't touching private members."""
    cl._view_loaded = True


def shell_hint(command: str) -> Panel:
    if os.name == "nt":
        shell_prefix = f"{os.getcwd()}>"
    else:
        shell_prefix = (
            f"{getpass.getuser()}@{socket.gethostname()}[bold green]$[/]"
        )
    return Panel.fit(f"{shell_prefix} {command}", title="Terminal")


def make_hint(
    comment: str | None = None,
    caller: Function | None | Iterable[Function] | str = None,
    *,
    line: int | None = None,
    prepend: str = "",
    back_lines: int = 1,
) -> Syntax | str:
    if not isinstance(caller, str):
        frame: Frame | None = inspect.currentframe()

        assert frame, "failed to get frame"

        back: Frame | None = frame.f_back
        assert back, "failed to get f_back"

        code_list = []

        if caller:
            if isinstance(caller, Iterable):
                code_list.extend(caller)
            else:
                code_list.append(caller.__code__)
        else:
            code_list.append(back.f_code)

        while back.f_back:
            back = back.f_back

            if back.f_code in code_list:
                break

        txt = pathlib.Path(back.f_code.co_filename).read_text(
            encoding="utf-8",
        )
        line = line or (back.f_lineno - back_lines)
    else:
        caller_path = pathlib.Path(caller)

        if not caller_path.exists():
            return ""

        txt = caller_path.read_text(encoding="utf-8")
        line = line or 0

    split = txt.split("\n")

    if comment:
        split[line] += f"{prepend}  # {comment}"

    return Syntax(
        "\n".join(split),
        "python",
        line_numbers=True,
        line_range=(line - 10, line + 20),
        highlight_lines={(line + 1) if not line < 0 else len(txt) - line},
    )


def attempt_import(name: str, *, repr_name: str | None = None) -> Module:
    Internal.info(f"attempting import: {name}")
    try:
        return importlib.import_module(name)
    except ImportError as e:
        raise MissingLibraryError(
            f"{repr_name or name} is not installed!",
            hint=shell_hint(f"pip install [bold]{name}[/]"),
        ) from e


_VALID_BODY = {str, int, type, dict, float, bool}


def validate_body(v: ViewBody) -> None:
    Internal.info(f"validating {v!r}")
    if type(v) not in _VALID_BODY:
        raise InvalidBodyError(
            f"{type(v).__name__} is not a valid type for a body",
        )

    if isinstance(v, dict):
        for i in v.values():
            validate_body(get_body(i))

    if isinstance(v, type):
        validate_body(get_body(v))


def get_body(tp: ViewBodyLike | Any) -> ViewBody:
    body_attr: ViewBody | None = getattr(tp, "__view_body__", None)

    if body_attr:
        if callable(body_attr):
            return body_attr()

        assert isinstance(body_attr, dict), "__view_body__ is not a dict"
        return body_attr

    return get_type_hints(tp)
