from __future__ import annotations

import asyncio
import getpass
import os
import random
import re
import subprocess
import venv as _venv
from inspect import iscoroutine
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from .routing import Route

import click

from .__about__ import __version__
from ._logging import VIEW_TEXT
from .build import run_build
from .exceptions import AppNotFoundError

B_OPEN = "{"
B_CLOSE = "}"

_GIT_EMAIL = re.compile(r' *email = "(.+)"')


def _get_email():
    home = Path.home()
    git_config = home / ".gitconfig"
    if not git_config.exists():
        return "your@email.com"

    try:
        text = git_config.read_text(encoding="utf-8")
    except PermissionError:
        return "your@email.com"

    for i in text.split("\n"):
        match = _GIT_EMAIL.match(i)
        if match:
            return match.group(1)

    return "your@email.com"


PYPROJECT_BASE = (
    lambda name: f"""[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
authors = [
    {B_OPEN}name = "{getpass.getuser()}", email = "{_get_email()}"{B_CLOSE}
]
requires-python = ">=3.8"
license = "MIT"
dependencies = ["view.py"]
version = "1.0.0"
"""
)


def success(msg: str) -> None:
    click.secho(f" - {msg}", fg="green", bold=True)


def warn(msg: str) -> None:
    click.secho(f" ! {msg}", fg="yellow", bold=True)


def error(msg: str) -> NoReturn:
    click.secho(f" ! {msg}", fg="red", bold=True)
    exit(1)


def info(msg: str) -> None:
    click.secho(f" * {msg}", fg="bright_magenta", bold=True)


def ver() -> None:
    click.echo(f"view.py {__version__}")


def welcome() -> None:
    click.secho(random.choice(VIEW_TEXT) + "\n", fg="blue", bold=True)
    ver()
    click.echo("Docs: ", nl=False)
    click.secho("https://view.zintensity.dev", fg="blue", bold=True)
    click.echo("GitHub: ", nl=False)
    click.secho(
        "https://github.com/ZeroIntensity/view.py",
        fg="green",
        bold=True,
    )
    click.echo("Support: ", nl=False)
    click.secho(
        "https://github.com/sponsors/ZeroIntensity",
        fg="bright_magenta",
        bold=True,
    )


@click.group(invoke_without_command=True)
@click.option("--debug", "-d", is_flag=True)
@click.option("--version", "-v", is_flag=True)
@click.pass_context
def main(ctx: click.Context, debug: bool, version: bool) -> None:
    if debug:
        from .util import enable_debug

        enable_debug()
    if version:
        ver()
    elif not ctx.invoked_subcommand:
        welcome()


@main.group()
def logs():
    ...


@logs.command()
@click.option(
    "--path",
    type=click.Path(
        exists=True,
        file_okay=False,
        resolve_path=True,
        path_type=Path,
        writable=True,
    ),
    default="./",
)
def show(path: Path):
    from rich import print
    from rich.panel import Panel

    internal = path / "view_internal.log"

    if not internal.exists():
        error(f"`{internal}` does not exist")

    service = path / "view_service.log"

    if not service.exists():
        error(f"`{service}` does not exist")

    print(Panel(internal.read_text(encoding="utf-8"), title=str(internal)))
    click.pause()
    print(Panel(service.read_text(encoding="utf-8"), title=str(service)))


@logs.command()
@click.option(
    "--path",
    type=click.Path(
        exists=True,
        file_okay=False,
        resolve_path=True,
        path_type=Path,
        writable=True,
    ),
    default="./",
)
def clear(path: Path):
    internal = path / "view_internal.log"

    if not internal.exists():
        error(f"`{internal}` does not exist")

    service = path / "view_service.log"

    if not service.exists():
        error(f"`{service}` does not exist")

    os.remove(internal)
    os.remove(service)


def _run(*, force_prod: bool = False) -> None:
    from .config import load_config
    from .util import run as run_path

    os.environ["_VIEW_RUN"] = "1"

    conf = load_config()
    if force_prod:
        conf.dev = True

    try:
        run_path(conf.app.app_path)
    except AppNotFoundError as e:
        error(str(e).replace('"', "`"))


@main.command()
def serve():
    _run()


@main.command()
def prod():
    _run(force_prod=True)


@main.command()
@click.option(
    "--target",
    type=click.Choice(("replit", "heroku", "nginx")),
    prompt="Where to deploy to",
)
def deploy(target: str):
    raise NotImplementedError


@main.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(
        exists=False,
        file_okay=False,
        resolve_path=True,
        path_type=Path,
        writable=True,
    ),
    default=Path.cwd() / "build",
)
def build(path: Path):
    from .config import load_config
    from .util import extract_path

    conf = load_config()
    app = extract_path(conf.app.app_path)
    app.load()

    run_build(app, path=path)


@main.command()
@click.option(
    "--name",
    "-n",
    help="Project name.",
    type=str,
    default="my_app",
    prompt="Project name",
)
@click.option(
    "--load",
    "-l",
    help="Preset for route loading.",
    default="simple",
    type=click.Choice(("manual", "filesystem", "simple", "patterns")),
    prompt="Loader strategy",
)
@click.option(
    "--repo",
    "-r",
    help="Whether a Git repository should be created.",
    default=True,
    is_flag=True,
    prompt="Create repository?",
)
@click.option(
    "--venv",
    help="Whether a virtual environment should be created.",
    default=True,
    is_flag=True,
    prompt="Create virtual environment?",
)
@click.option(
    "--path",
    "-p",
    type=click.Path(
        exists=False,
        file_okay=False,
        resolve_path=True,
        path_type=Path,
        writable=True,
    ),
    default=None,
)
@click.option(
    "--type",
    "-t",
    help="Configuration type to initalize.",
    default="toml",
    type=click.Choice(("toml", "json", "ini", "yml", "py")),
)
@click.option(
    "--no-project",
    help="Disable creation of a pyproject.toml file.",
    is_flag=True,
)
def init(
    name: str,
    repo: bool,
    venv: bool,
    path: Path | None,
    type: str,
    load: str,
    no_project: bool,
):
    from .config import make_preset

    path = path or Path(f"./{name}")

    fname = f"view.{type}"
    if not path.exists():
        success(f"Created `{path.relative_to('.')}`")
        path.mkdir()

    if repo:
        info("Initializing repository...")
        res = subprocess.call(["git", "init", str(path)])
        if res != 0:
            warn("failed to initalize git repository")

    if venv:
        info("Creating venv...")
        venv_path = path / ".venv"
        _venv.create(venv_path, with_pip=True)
        success(f"Created virtual environment in {venv_path}")
        info("Installing view.py...")
        res = subprocess.call(
            [(venv_path / "bin" / "pip").absolute(), "install", "view.py"]
        )

        if res != 0:
            error("failed to install view.py")

    conf_path = path / fname
    with open(conf_path, "w") as f:
        f.write(make_preset(type, load))

    success(f"Created `{fname}`")

    app_path = path / "app.py"

    from .__about__ import __version__

    with open(app_path, "w") as f:
        if load in {"filesystem", "simple", "patterns"}:
            f.write(
                f"# view.py {__version__}\n"
                """from view import new_app

app = new_app()
app.run()
"""
            )

        if load == "manual":
            f.write(
                f"# view.py {__version__}\n"
                """from view import new_app

app = new_app()

@app.get("/")
async def index():
    return "Hello, view.py!"

app.run()
"""
            )

    success("Created `app.py`")

    if not no_project:
        pyproject = path / "pyproject.toml"

        with pyproject.open("w", encoding="utf-8") as f:
            f.write(PYPROJECT_BASE(name))

        success("Created `pyproject.toml`")

    if load == "patterns":
        urls = path / "urls.py"
        with open(urls, "w") as f:
            f.write(
                """from view import path
from routes.index import index

PATTERNS = (
    path("/", index),
)
"""
            )

    if load != "manual":
        routes = path / "routes"
        routes.mkdir()
        success("Created `routes`")

        index = routes / "index.py"

        pathstr = "" if load == "filesystem" else "'/'"
        with open(index, "w") as f:
            f.write(
                f"""from view import get

@get({pathstr})
async def index():
    return 'Hello, view.py!'
"""
            )

            success("Created `routes/index.py`")

    welcome()
    success(f"Successfully initalized app in `{path}`")
    return


@main.command()
@click.option(
    "--file",
    "-f",
    type=click.Path(
        exists=False,
        dir_okay=False,
        resolve_path=True,
        path_type=Path,
        writable=True,
    ),
    default=Path.cwd() / "docs.md",
)
@click.option("--app", "-a", type=str, default=None)
def docs(file: Path, app: str | None):
    from .config import load_config
    from .util import extract_path

    if not app:
        conf = load_config()
        target = extract_path(conf.app.app_path)
    else:
        target = extract_path(app)

    target.docs(file)
    success(f"Created `{file}`")


if __name__ == "__main__":
    main()
