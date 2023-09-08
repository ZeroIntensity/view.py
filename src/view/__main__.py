from __future__ import annotations
import getpass
import os
import re
from pathlib import Path

import click

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
requires-python = ">=3.7"
license = "MIT"
dependencies = ["view.py", "uvicorn"]
version = "1.0.0"
"""
)


def success(msg: str) -> None:
    click.secho(msg, fg="green", bold=True)


def warn(msg: str) -> None:
    click.secho(msg, fg="yellow", bold=True)


def error(msg: str) -> None:
    click.secho(msg, fg="red", bold=True)
    exit(1)


def should_continue(msg: str):
    if not click.confirm(
        click.style(
            msg,
            fg="yellow",
        )
    ):
        exit(2)


@click.group(invoke_without_command=True)
@click.option("--debug", "-d", is_flag=True)
@click.pass_context
def main(ctx: click.Context, debug: bool) -> None:
    if debug:
        from .util import debug as enable_debug

        enable_debug()
    elif not ctx.invoked_subcommand:
        click.secho("Welcome to view.py!", fg="green", bold=True)
        click.echo("Docs: ", nl=False)
        click.secho("https://view.zintensity.dev", fg="blue", bold=True)
        click.echo("GitHub: ", nl=False)
        click.secho(
            "https://github.com/ZeroIntensity/view.py",
            fg="blue",
            bold=True,
        )


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
    run_path(conf.app.app_path)


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
    default="./",
    prompt="Path to initialize to",
)
@click.option(
    "--type",
    "-t",
    help="Configuration type to initalize.",
    default="toml",
    type=click.Choice(("toml", "json", "ini", "yml", "py")),
)
@click.option(
    "--load",
    "-l",
    help="Preset for route loading.",
    default="filesystem",
    type=click.Choice(("manual", "filesystem", "simple")),
    prompt="Loader strategy",
)
@click.option(
    "--no-project",
    help="Disable creation of a pyproject.toml file.",
    is_flag=True,
)
@click.option(
    "--name",
    "-n",
    help="Project name to be used in configuration.",
    type=str,
    default="my_app",
)
def init(path: Path, type: str, load: str, no_project: bool, name: str):
    from .config import make_preset

    fname = f"view.{type}"
    if not path.exists():
        path.mkdir()

    conf_path = path / fname
    if conf_path.exists():
        should_continue(f"`{conf_path}` already exists, overwrite?")

    with open(conf_path, "w") as f:
        f.write(make_preset(type, load))

    click.echo(f"Created `{fname}`")

    app_path = path / "app.py"

    if app_path.exists():
        should_continue(f"`{app_path}` already exists, overwrite?")

    from .__about__ import __version__

    with open(app_path, "w") as f:
        if load in {"filesystem", "simple"}:
            f.write(
                f"# view.py {__version__}"
                """
import view

app = view.new_app()
app.run()
"""
            )

        if load == "manual":
            f.write(
                f"# view.py {__version__}"
                """
import view
from routes.index import index

app = view.new_app()

app.load([index])
app.run()
"""
            )

    click.echo("Created `app.py`")

    if not no_project:
        pyproject = path / "pyproject.toml"

        if pyproject.exists():
            should_continue("`pyproject.toml` already exists, overwrite?")
        else:
            with pyproject.open("w", encoding="utf-8") as f:
                f.write(PYPROJECT_BASE(name))

            click.echo("Created `pyproject.toml`")

    scripts = path / "scripts"

    if scripts.exists():
        should_continue("`scripts` already exists, overwrite?")
    else:
        scripts.mkdir()
        click.echo("Created `scripts`")

    routes = path / "routes"
    if routes.exists():
        should_continue("`routes` already exists, overwrite?")
    else:
        routes.mkdir()
        click.echo("Created `routes`")

    index = routes / "index.py"

    if index.exists():
        should_continue(
            f"`{index.relative_to('.')}` already exists, overwrite?"
        )
    pathstr = "" if load == "filesystem" else "'/'"
    with open(index, "w") as f:
        f.write(
            f"""from view.routing import get

@get({pathstr})
async def index():
    return 'Hello, view.py!'
"""
        )

        click.echo("Created `routes/index.py`")

    success(f"Successfully initalized app in `{path}`")
    return


if __name__ == "__main__":
    main()
