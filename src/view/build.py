"""
view.py build APIs

While this module is considered public, you likely don't need the functions in here.
Instead, you should just let view.py do most of the work, such as through calling `build_app` upon startup.
"""

from __future__ import annotations

import asyncio
import importlib
import re
import runpy
import warnings
from asyncio import subprocess
from collections.abc import Coroutine
from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple, NoReturn

import aiofiles
import aiofiles.os

from ._logging import Internal
from .app import App
from .typing import ViewResult

if TYPE_CHECKING:
    from .config import Config

import platform

from .config import BuildStep, Platform
from .exceptions import (
    BuildError,
    BuildWarning,
    MissingRequirementError,
    PlatformNotSupportedError,
    UnknownBuildStepError,
    ViewInternalError,
)
from .util import to_response

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


async def _call_script(path: Path, *, call_func: str | None = None) -> Any:
    Internal.info(f"Executing Python script at `{path}`")
    globls = runpy.run_path(str(path), run_name="__view_build__")

    if call_func:
        func = globls.get(call_func)
        if func:
            try:
                return await func()
            except Exception as e:
                raise BuildError(f"Script at {path} raised exception!") from e


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
    "pipx",
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
            res = await reqfunc()
            if res is False:
                raise MissingRequirementError(
                    f"Requirement script in module {target} returned non-True"
                )
    elif prefix == "script":
        path = Path(target)
        if (not path.exists()) or (not path.is_file()):
            raise MissingRequirementError(
                f"Python script at {target} does not exist or is not a file"
            )

        res = await _call_script(path, call_func="__view_requirement__")
        if res is False:
            raise MissingRequirementError(
                f"Requirement script at {path} returned non-True"
            )
    elif prefix == "path":
        if not Path(target).exists():
            raise MissingRequirementError(f"{target} does not exist")
    elif prefix == "command":
        if not await _check_version_command(target):
            raise MissingRequirementError(f"{target} is not installed")
    else:
        raise BuildError(f"Invalid requirement prefix: {prefix}")


_PLATFORMS: dict[str, list[Platform]] = {
    "Linux": ["linux", "Linux"],
    "Darwin": ["mac", "macOS", "Mac", "MacOS"],
    "Windows": ["windows", "Windows"],
}


def _is_platform_compatible(plat: Platform | list[Platform] | None) -> bool:
    system = platform.system()

    try:
        names = _PLATFORMS[system]
    except KeyError as e:
        raise ViewInternalError(
            f"platform.system() returned unknown os: {system}"
        ) from e

    if isinstance(plat, list):
        for supported_platform in plat:
            if supported_platform in names:
                return True

        return False

    return plat in names


def _invalid_platform(name: str) -> NoReturn:
    system = platform.system()
    raise PlatformNotSupportedError(
        f"build step {name!r} does not support {system.lower()}"
    )


async def _build_step(step: _BuildStepWithName) -> None:
    if step.step.platform:
        if not _is_platform_compatible(step.step.platform):
            _invalid_platform(step.name)

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
                await _call_script(script, call_func="__view_build__")
        else:
            await _call_script(data.script, call_func="__view_build__")


def _find_step(name: str, steps: list[BuildStep]) -> _BuildStepWithName:
    platform_step: _BuildStepWithName | None = None
    null_platform: bool = False

    for i in steps:
        if (not i.platform) and (not platform_step):
            if null_platform:
                raise BuildError(
                    f"step {name!r} has multiple entries without a platform"
                )
            platform_step = _BuildStepWithName(name, i, [])
            null_platform = True
        else:
            if _is_platform_compatible(i.platform):
                platform_step = _BuildStepWithName(name, i, [])

    if not platform_step:
        _invalid_platform(name)

    return platform_step


async def run_step(app_or_config: App | Config, name: str) -> None:
    """
    Run an individual build step.

    Args:
        app: App object or configuration to load build steps from.
        name: Name of the build step.

    Raises:
        UnknownBuildStepError: The step does not exist.
    """
    if isinstance(app_or_config, App):
        step_conf = app_or_config.config.build.steps.get(name)
    else:
        step_conf = app_or_config.build.steps.get(name)

    if not step_conf:
        raise UnknownBuildStepError(f"no step named {name!r}")

    if isinstance(step_conf, list):
        step = _find_step(name, step_conf)
    else:
        step = _BuildStepWithName(name, step_conf, [])

    await _build_step(step)


async def build_steps(app_or_config: App | Config) -> None:
    """
    Run the default build steps for a given application or configuration. This is called upon starting a server.

    Args:
        app_or_config: App or configuration object to read build steps from.
    """
    if isinstance(app_or_config, App):
        build = app_or_config.config.build
    else:
        build = app_or_config.build

    cache: list[str] = []
    steps: list[_BuildStepWithName] = []

    for name, step in build.steps.items():
        if build.default_steps and (name not in build.default_steps):
            continue

        if isinstance(step, list):
            steps.append(_find_step(name, step))
        else:
            steps.append(_BuildStepWithName(name, step, cache))

    Internal.info("Starting build steps")

    if build.parallel:
        coros = [_build_step(step) for step in steps]
        await asyncio.gather(*coros)
    else:
        for step in steps:
            await _build_step(step)


async def _handle_result(res: ViewResult) -> str | bytes:
    response = await to_response(res)
    return response.body


async def _compile_routes(
    app: App,
    *,
    should_await: bool = False,
) -> dict[str, str | bytes]:
    from .routing import Method

    results: dict[str, str | bytes] = {}
    coros: list[Coroutine] = []

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

        res = i.func()  # type: ignore

        # I'm unsure if I'm doing this right.
        # Reviewers, correct this if I'm wrong!
        if isinstance(res, Coroutine):
            if should_await:
                results[i.path[1:]] = await _handle_result(await res)
            else:
                task = asyncio.create_task(res)

                def cb(fut: asyncio.Task[ViewResult]):
                    text = fut.result()

                    def cb_2(fut2: asyncio.Task[str | bytes]):
                        assert i.path is not None
                        results[i.path[1:]] = fut2.result()

                    task2 = asyncio.create_task(_handle_result(text))
                    task2.add_done_callback(cb_2)

                task.add_done_callback(cb)
                coros.append(res)

    if not should_await:
        await asyncio.gather(*coros)

    return results


async def build_app(app: App, *, path: Path | None = None) -> None:
    """
    Compile an app into static HTML, including running all of it's build steps.

    Args:
        app: App object to build.
        path: Output path for files.
    """
    Internal.info("Starting build process!")
    await build_steps(app)

    Internal.info("Getting routes")
    results = await _compile_routes(
        app,
        should_await=not app.config.build.parallel,
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

        if isinstance(content, str):
            async with aiofiles.open(file, "w", encoding="utf-8") as f:
                await f.write(content)
        else:
            async with aiofiles.open(file, "wb") as f:
                await f.write(content)
        Internal.info(f"Created {file}")

    Internal.info("Successfully built app")
