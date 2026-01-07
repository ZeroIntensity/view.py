"""
This is mostly stolen from CPython's _colorize module. If that becomes part of
the standard library someday, we can hopefully remove this.
"""

import logging
import os
import sys
from typing import IO


class ANSIColors:
    """
    Namespace of ANSI color codes.
    """

    RESET = "\x1b[0m"

    BLACK = "\x1b[30m"
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    GREY = "\x1b[90m"
    MAGENTA = "\x1b[35m"
    RED = "\x1b[31m"
    WHITE = "\x1b[37m"  # more like LIGHT GRAY
    YELLOW = "\x1b[33m"

    BOLD = "\x1b[1m"
    BOLD_BLACK = "\x1b[1;30m"  # DARK GRAY
    BOLD_BLUE = "\x1b[1;34m"
    BOLD_CYAN = "\x1b[1;36m"
    BOLD_GREEN = "\x1b[1;32m"
    BOLD_MAGENTA = "\x1b[1;35m"
    BOLD_RED = "\x1b[1;31m"
    BOLD_WHITE = "\x1b[1;37m"  # actual WHITE
    BOLD_YELLOW = "\x1b[1;33m"

    # intense = like bold but without being bold
    INTENSE_BLACK = "\x1b[90m"
    INTENSE_BLUE = "\x1b[94m"
    INTENSE_CYAN = "\x1b[96m"
    INTENSE_GREEN = "\x1b[92m"
    INTENSE_MAGENTA = "\x1b[95m"
    INTENSE_RED = "\x1b[91m"
    INTENSE_WHITE = "\x1b[97m"
    INTENSE_YELLOW = "\x1b[93m"

    BACKGROUND_BLACK = "\x1b[40m"
    BACKGROUND_BLUE = "\x1b[44m"
    BACKGROUND_CYAN = "\x1b[46m"
    BACKGROUND_GREEN = "\x1b[42m"
    BACKGROUND_MAGENTA = "\x1b[45m"
    BACKGROUND_RED = "\x1b[41m"
    BACKGROUND_WHITE = "\x1b[47m"
    BACKGROUND_YELLOW = "\x1b[43m"

    INTENSE_BACKGROUND_BLACK = "\x1b[100m"
    INTENSE_BACKGROUND_BLUE = "\x1b[104m"
    INTENSE_BACKGROUND_CYAN = "\x1b[106m"
    INTENSE_BACKGROUND_GREEN = "\x1b[102m"
    INTENSE_BACKGROUND_MAGENTA = "\x1b[105m"
    INTENSE_BACKGROUND_RED = "\x1b[101m"
    INTENSE_BACKGROUND_WHITE = "\x1b[107m"
    INTENSE_BACKGROUND_YELLOW = "\x1b[103m"


NoColors = ANSIColors()

for attr, code in ANSIColors.__dict__.items():
    if not attr.startswith("__"):
        setattr(NoColors, attr, "")


def _supports_colors(*, file: IO[str] | IO[bytes] | None = None) -> bool:
    """
    Does the current environment support ANSI color codes?
    """

    if file is None:
        file = sys.stdout

    assert file is not None
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("TERM") == "dumb":
        return False

    if not hasattr(file, "fileno"):
        return False

    if sys.platform == "win32":
        try:
            import nt

            if not nt._supports_virtual_terminal():
                return False
        except (ImportError, AttributeError):
            return False

    try:
        return os.isatty(file.fileno())
    except OSError:
        return hasattr(file, "isatty") and file.isatty()


def get_colors(*, file: IO[str] | IO[bytes] | None = None) -> ANSIColors:
    """
    Get a namespace containing color names as attributes. If colors are
    enabled, these attributes will contain ANSI color codes. Otherwise, they'll
    be empty string.

    """
    if _supports_colors(file=file):
        return ANSIColors()
    return NoColors


class ColorfulFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        colors = get_colors()
        mapping = {
            logging.DEBUG: colors.BOLD_BLUE,
            logging.INFO: colors.BOLD_GREEN,
            logging.WARNING: colors.BOLD_YELLOW,
            logging.ERROR: colors.BOLD_RED,
            logging.CRITICAL: colors.INTENSE_BACKGROUND_RED,
        }
        color_code = mapping.get(record.levelno)
        if color_code is not None:
            record.levelname = f"{color_code}{record.levelname}{colors.RESET}"

        return super().format(record)
