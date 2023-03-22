from __future__ import annotations

import logging
import os
import runpy
<<<<<<< HEAD
import sys
from typing import TYPE_CHECKING, NoReturn
=======
import weakref
from typing import NoReturn
>>>>>>> 66149dc2a4df2669358dbe834af3963c353649c6

from ._logging import Internal, Service

if TYPE_CHECKING:
    from .app import App


def run(app_or_path: str | App) -> NoReturn:
    from .app import App

    if isinstance(app_or_path, App):
        app_or_path.run()

    split = app_or_path.split(":", maxsplit=1)

    if len(split) != 2:
        raise ValueError(
            "module string should be in the format of `/path/to/app.py:app`",
        )

    path = os.path.abspath(split[0])
    sys.path.append(os.path.dirname(path))

    try:
        mod = runpy.run_path(path)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f'"{split[0]}" in {app_or_path} does not exist'
        ) from e

    try:
        target = mod[split[1]]
    except KeyError:
        raise AttributeError(
            f'"{split[1]}" in {app_or_path} does not exist'
        ) from None

    if not isinstance(target, App):
        raise TypeError(f"{target!r} is not an instance of view.App")

    target._run()
    exit(0)


def debug():
    internal = Internal.log
    internal.disabled = False
    internal.setLevel(logging.DEBUG)
    internal.addHandler(
        logging.FileHandler("view_internal.log", mode="w", encoding="utf-8")
    )
    Service.log.addHandler(
        logging.FileHandler("view_service.log", mode="w", encoding="utf-8")
    )

    Internal.info("debug mode enabled")
    os.environ["VIEW_DEBUG"] = "1"
