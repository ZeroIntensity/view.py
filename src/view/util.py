from __future__ import annotations

import os
import runpy
from typing import NoReturn

from .app import App


def run(app_or_path: str | App) -> NoReturn:
    if isinstance(app_or_path, App):
        app_or_path.run()

    split = app_or_path.split(":", maxsplit=1)

    if len(split) != 2:
        raise ValueError(
            "module string should be in the format of `/path/to/app.py:app`",
        )

    try:
        mod = runpy.run_path(os.path.abspath(split[0]))
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f'"{split[0]}" in {app_or_path} does not exist'
        ) from e

    try:
        target = mod[split[1]]
    except KeyError as e:
        raise AttributeError(
            f'"{split[1]}" in {app_or_path} does not exist'
        ) from e

    if not isinstance(target, App):
        raise TypeError(f"{target!r} is not an instance of view.App")

    target._run()
    exit(0)
