from __future__ import annotations

import asyncio
import importlib
import re
import runpy
import warnings
from asyncio import subprocess
from collections.abc import Coroutine
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import aiofiles
import aiofiles.os

from ._logging import Internal
from .typing import ViewResult

if TYPE_CHECKING:
    from .app import App

from .config import BuildStep
from .exceptions import BuildError, BuildWarning, MissingRequirementError
from .response import to_response

__all__ = "build_steps", "build_app"


class _BuildStepWithName(NamedTuple):
    name: str
    step: BuildStep
    cache: list[str]


_SPECIAL_REQ = re.compile(r"(\w+)\+(.+)")


async def _call_command(command: str) -> None:
    Internal.info(f"Running `{command}`")
    proc = await subprocess.create_subprocess_shell(command)
    await proc.wait()

    if proc.returncode != 0:
        raise BuildError(f"{command} returned non-zero exit code")


async def _call_script(path: Path, *, call_func: str | None = None) -> None:
    Internal.info(f"Executing Python script at `{path}`")
    globls = runpy.run_path(str(path), run_name="__view_build__")

    if call_func:
        func = globls.get(call_func)
        if func:
            await func()


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


async def _check_version_command(name: str) -> bool:
    command = "--version"

    if name in _USE_V_FLAG:
        command = "-v"

    if name in _USE_SINGLE_DASH:
        command = "-version"

    proc = await subprocess.create_subprocess_shell(
        f"{name} {command}",
        stdout=subprocess.PIPE,
    )
    await proc.wait()
    return proc.returncode == 0


async def _check_requirement(req: str) -> None:
    Internal.info(f"Ensuring dependency {req!r}")
    special = _SPECIAL_REQ.match(req)

    if not special:
        if req not in _COMMAND_REQS:
            raise BuildError(f"Unknown build requirement: {req!r}")

        if not await _check_version_command(req):
            raise MissingRequirementError(f"{req} is not installed")
        return

    prefix = special.group(1)
    target = special.group(2)

    if prefix == "mod":
        Internal.info(f"Importing `{target}`")
        try:
            mod = importlib.import_module(target)
        except ModuleNotFoundError as e:
            raise MissingRequirementError(f"Could not import {target}") from e

        reqfunc = getattr(mod, "__view_requirement__", None)
        if reqfunc:
            await reqfunc
    elif prefix == "script":
        path = Path(target)
        if (not path.exists()) or (not path.is_file()):
            raise MissingRequirementError(
                f"Python script at {target} does not exist or is not a file"
            )

        await _call_script(path)
    elif prefix == "path":
        if not Path(target).exists():
            raise MissingRequirementError(f"{target} does not exist")
    else:
        raise BuildError(f"Invalid requirement prefix: {prefix}")


async def _build_step(step: _BuildStepWithName) -> None:
    Internal.info(f"Building step {step.name!r}")
    data = step.step

    for req in data.requires:
        if req in step.cache:
            Internal.info(f"{req} was already checked, skipping it")
            continue

        await _check_requirement(req)
        step.cache.append(req)

    if data.command:
        if isinstance(data.command, list):
            for command in data.command:
                await _call_command(command)
        else:
            await _call_command(data.command)

    if data.script:
        if isinstance(data.script, list):
            for script in data.script:
                await _call_script(script)
        else:
            await _call_script(data.script)


async def run_step(app: App, name: str) -> None:
    """Run an individual build step."""
    step = _BuildStepWithName(name, app.config.build.steps[name], [])
    await _build_step(step)


async def build_steps(app: App) -> None:
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

    if app.config.build.parallel:
        coros = [_build_step(step) for step in steps]
        await asyncio.gather(*coros)
    else:
        for step in steps:
            await _build_step(step)


def _handle_result(res: ViewResult) -> str:
    response = to_response(res)
    return response.body


async def _compile_routes(
    app: App, *, should_await: bool = False
) -> dict[str, str]:
    from .routing import Method

    results: dict[str, str] = {}
    coros: list[Coroutine] = []

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
            if should_await:
                results[i.path[1:]] = _handle_result(await res)
            else:
                task = asyncio.create_task(res)

                def cb(fut: asyncio.Task[ViewResult]):
                    text = fut.result()
                    assert i.path is not None
                    results[i.path[1:]] = _handle_result(text)

                task.add_done_callback(cb)
                coros.append(res)

    if not should_await:
        await asyncio.gather(*coros)

    return results


async def build_app(app: App, *, path: Path | None = None) -> None:
    """Compile an app into static HTML, including running all of it's build steps."""
    Internal.info("Starting build process!")
    await build_steps(app)

    Internal.info("Getting routes")
    results = await _compile_routes(
        app, should_await=not app.config.build.parallel
    )
    path = path or app.config.build.path

    if path.exists():
        await aiofiles.os.removedirs(path)
        await aiofiles.os.mkdir(path)
    elif not path.exists():
        await aiofiles.os.mkdir(path)

    for file_path, content in results.items():
        directory = path / file_path
        file = directory / "index.html"

        if not (await aiofiles.os.path.exists(directory)):
            await aiofiles.os.mkdir(directory)
            Internal.info(f"Created {directory}")

        async with aiofiles.open(file, "w", encoding="utf-8") as f:
            await f.write(content)
        Internal.info(f"Created {file}")

    Internal.info("Successfully built app")
