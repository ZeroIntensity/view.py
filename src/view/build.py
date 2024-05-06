from __future__ import annotations

import asyncio
import warnings
from inspect import iscoroutine
from pathlib import Path

from ._logging import Internal
from .app import App
from .config import BuildStep
from .exceptions import BuildError, BuildWarning
from .routing import Method


def run_steps(app: App) -> None:
    build = app.config.build
    steps: list[BuildStep]

    if build.default_steps is None:
        ...

    Internal.info("Starting build steps")


def run_build(app: App, *, path: Path | None) -> None:
    results: dict[str, str] = {}
    Internal.info("Starting build process!")
    run_steps(app)

    Internal.info("Getting routes")
    for i in app.loaded_routes:
        if (not i.method) or (i.method != Method.GET):
            warnings.warn(f"{i} is not a GET route, skipping it", BuildWarning)
            continue

        if not i.path:
            warnings.warn(f"{i} needs path parameters, skipping it", BuildWarning)
            continue

        Internal.info(f"Calling GET {i.path}")

        if i.inputs:
            warnings.warn(f"{i.path} needs a route input, skipping it", BuildWarning)
            continue

        res = i.func()

        if iscoroutine(res):
            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(res)

        text: str

        if hasattr(res, "__view_response__"):
            res = res.__view_response__()  # type: ignore

        if isinstance(res, tuple):
            for x in res:
                if isinstance(x, str):
                    text = x
                    break
            raise BuildError(f"{i.path} didn't return a response")
        else:
            text = res  # type: ignore

        assert i.path
        results[i.path[1:]] = text
        Internal.info(f"Got response for {i.path}")

    path = path or Path.cwd() / "build"

    if path.exists():
        raise BuildError(f"{path} already exists")

    path.mkdir()

    for file_path, content in results.items():
        directory = path / file_path
        file = directory / "index.html"
        directory.mkdir(exist_ok=True)
        Internal.info(f"Created {directory}")
        file.write_text(content, encoding="utf-8")
        Internal.info(f"Created {file}")

    Internal.info("Successfully built app")
