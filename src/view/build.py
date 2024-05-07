from __future__ import annotations

import asyncio
import importlib
import re
import runpy
import shlex
import shutil
import subprocess
import warnings
from collections.abc import Coroutine
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from ._logging import Internal

if TYPE_CHECKING:
    from .app import App

from .config import BuildStep
from .exceptions import BuildError, BuildWarning, MissingRequirementError
from .routing import Method

__all__ = "run_step", "build_steps", "build_app"


class _BuildStepWithName(NamedTuple):
    name: str
    step: BuildStep
    cache: list[str]


_SPECIAL_REQ = re.compile(r"(\w+)\+(.+)")


def _call_command(command: str) -> None:
    Internal.info(f"Running `{command}`")
    subprocess.call(shlex.split(command))


def _call_script(path: Path) -> None:
    Internal.info(f"Executing Python script at `{path}`")
    runpy.run_path(str(path), run_name="__view_build__")


_COMMAND_REQS = [
    # C
    "gcc",
    "cl",
    "clang",
    # C++
    "g++",
    "clang++",
    "cmake",
    # Python
    "pip",
    "uv",
    "poetry",
    # JavaScript
    "node",
    "npm",
    "yarn",
    "pnpm",
    "bun",
    # Java
    "java",
    "javac",
    "mvn",
    "gradle",
    "gradlew",
    # Rust
    "rustup",
    "rustc",
    "cargo",
    # Ruby
    "gem",
    "ruby",
    # C#
    "dotnet",
    "nuget",
    # PHP
    "php",
    "composer",
    # Go
    "go",
    # Kotlin
    "kotlinc",
    # Lua
    "lua",
    "luarocks",
    # Dart
    "dart",
]

# use -v
_USE_V_FLAG = ["lua", "php"]
# use -version
_USE_SINGLE_DASH = ["kotlinc", "java", "javac"]


def _check_version_command(name: str) -> bool:
    command = "--version"

    if name in _USE_V_FLAG:
        command = "-v"

    if name in _USE_SINGLE_DASH:
        command = "-version"

    return (
        subprocess.check_call(
            [name, command],
            stdout=subprocess.PIPE,
        )
        == 0
    )


def _check_requirement(req: str) -> None:
    Internal.info(f"Ensuring dependency {req!r}")
    special = _SPECIAL_REQ.match(req)

    if not special:
        if req not in _COMMAND_REQS:
            raise BuildError(f"Unknown build requirement: {req!r}")

        if not _check_version_command(req):
            raise MissingRequirementError(f"{req} is not installed")
        return

    prefix = special.group(1)
    target = special.group(2)

    if prefix == "mod":
        Internal.info(f"Importing `{target}`")
        try:
            importlib.import_module(target)
        except ModuleNotFoundError as e:
            raise MissingRequirementError(f"Could not import {target}") from e
    elif prefix == "script":
        path = Path(target)
        if (not path.exists()) or (not path.is_file()):
            raise MissingRequirementError(
                f"Python script at {target} does not exist or is not a file"
            )

        _call_script(path)
    elif prefix == "path":
        if not Path(target).exists():
            raise MissingRequirementError(f"{target} does not exist")
    else:
        raise BuildError(f"Invalid requirement prefix: {prefix}")


def _build_step(step: _BuildStepWithName) -> None:
    Internal.info(f"Building step {step.name!r}")
    data = step.step

    for req in data.requires:
        if req in step.cache:
            Internal.info(f"{req} was already checked, skipping it")
            continue

        _check_requirement(req)
        step.cache.append(req)

    if data.command:
        if isinstance(data.command, list):
            for command in data.command:
                _call_command(command)
        else:
            _call_command(data.command)

    if data.script:
        if isinstance(data.script, list):
            for script in data.script:
                _call_script(script)
        else:
            _call_script(data.script)


def run_step(app: App, name: str) -> None:
    """Run an individual build step."""
    step = _BuildStepWithName(name, app.config.build.steps[name], [])
    _build_step(step)


def build_steps(app: App) -> None:
    """Run the default build steps for a given application."""
    build = app.config.build
    cache: list[str] = []

    steps: list[_BuildStepWithName] = (
        [
            _BuildStepWithName(name, step, cache)
            for name, step in build.steps.items()
        ]
        if build.default_steps is None
        else [
            _BuildStepWithName(name, step, cache)
            for name, step in build.steps.items()
            if name in build.default_steps
        ]
    )

    Internal.info("Starting build steps")

    for step in steps:
        _build_step(step)


def build_app(app: App, *, path: Path | None = None) -> None:
    """Compile an app into static HTML, including running all of it's build steps."""
    results: dict[str, str] = {}
    Internal.info("Starting build process!")
    build_steps(app)

    Internal.info("Getting routes")
    for i in app.loaded_routes:
        if (not i.method) or (i.method != Method.GET):
            warnings.warn(f"{i} is not a GET route, skipping it", BuildWarning)
            continue

        if not i.path:
            warnings.warn(
                f"{i} needs path parameters, skipping it", BuildWarning
            )
            continue

        Internal.info(f"Calling GET {i.path}")

        if i.inputs:
            warnings.warn(
                f"{i.path} needs a route input, skipping it", BuildWarning
            )
            continue

        res = i.func()

        if isinstance(res, Coroutine):
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

    path = path or app.config.build.path

    if path.exists():
        shutil.rmtree(str(path))
        path.mkdir()
    elif not path.exists():
        path.mkdir()

    for file_path, content in results.items():
        directory = path / file_path
        file = directory / "index.html"
        directory.mkdir(exist_ok=True)
        Internal.info(f"Created {directory}")
        file.write_text(content, encoding="utf-8")
        Internal.info(f"Created {file}")

    Internal.info("Successfully built app")
