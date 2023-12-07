import importlib.metadata
import subprocess
from io import StringIO

from rich import print
from versions import parse_version, parse_version_set

from .exceptions import InstallationError

__all__ = ("install", "check_dep", "ensure_dep")


def install(name: str) -> None:
    try:
        print(f"[bold green] * Installing {name}...[/]")
        subprocess.check_call(["pip", "install", name])
    except subprocess.CalledProcessError as e:
        raise InstallationError(f"failed to install `{name}` via pip") from e

    print(
        f"[bold green] * View has installed {name} in your current environment[/]",  # noqa
    )


def check_dep(name: str) -> bool:
    dep_name_io = StringIO()
    version_io = StringIO()
    target_io = dep_name_io

    for i in name:
        if i in {">", "<", "^", "@", "="}:
            target_io = version_io

        target_io.write(i)

    dep_name = dep_name_io.getvalue()
    version_str = version_io.getvalue().replace("@", "==")

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


def ensure_dep(name: str) -> None:
    if not check_dep(name):
        install(name.replace("@", "=="))
