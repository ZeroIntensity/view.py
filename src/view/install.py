from __future__ import annotations
import asyncio
import importlib.metadata
import subprocess
from io import StringIO

from rich import print
from versions import parse_version, parse_version_set

from .exceptions import InstallationError

__all__ = (
    "install",
    "check_dep",
    "ensure_dep",
    "needs",
)


async def install(name: str) -> None:
    print(f"[bold green] * Installing {name}...[/]")
    try:
        await asyncio.to_thread(
            subprocess.check_call,
            ["pip", "install", name],
        )
    except subprocess.CalledProcessError as e:
        raise InstallationError(f"failed to install {name}: {e}") from e

    print(
        f"[bold green] * View has installed {name} in your current environment[/]",  # noqa
    )


def _get_parts(name: str) -> tuple[str, str]:
    dep_name_io = StringIO()
    version_io = StringIO()
    target_io = dep_name_io

    for i in name:
        if i in {">", "<", "^", "@", "="}:
            target_io = version_io

        target_io.write(i)

    return dep_name_io.getvalue(), version_io.getvalue()


def check_dep(name: str) -> bool:
    name = name.replace("@", "==")
    dep_name, version_str = _get_parts(name)
    if not version_str:
        version = parse_version_set("*")
    else:
        version = parse_version_set(version_str)

    try:
        return version.contains(
            parse_version(
                importlib.metadata.version(dep_name),
            ),
        )
    except importlib.metadata.PackageNotFoundError:
        return False


async def needs(name: str) -> None:
    from .app import get_app
    name = name.replace("@", "==")

    if not check_dep(name):
        app = get_app()
        if not app.config.auto_install:
            raise ModuleNotFoundError(
                f"view.py needs {name}, but auto_install is set to false",
            )

        await install(name)


async def ensure_dep(name: str) -> None:
    if not check_dep(name):
        await install(name.replace("@", "=="))
