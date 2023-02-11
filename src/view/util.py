from __future__ import annotations

import importlib
from typing import NoReturn

from .app import App


def run(app_or_mod: str | App) -> NoReturn:
    if isinstance(app_or_mod, App):
        app_or_mod.run()

    split = app_or_mod.split(maxsplit=1)

    if len(split) != 2:
        raise ValueError(
            "module string should be in the format of `a.b.c:app`",
        )

    mod = importlib.import_module(split[0])
    target = getattr(mod, split[1])

    if not isinstance(target, App):
        raise TypeError(f"{target!r} is not an instance of view.App")

    target.run()
