import os
from pathlib import Path

import click


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


@click.group()
@click.option("--debug", "-d", is_flag=True)
def main(debug: bool):
    if debug:
        from .util import debug as enable_debug

        enable_debug()


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


@main.command()
def serve():
    from .config import load_config
    from .util import run as run_path

    os.environ["_VIEW_RUN"] = "1"

    conf = load_config()
    run_path(conf.app.path)


@main.command()
@click.option(
    "--target",
    type=click.Choice(("replit", "heroku", "nginx", "cpanel")),
    prompt="Where to deploy to",
)
def deploy(target: str):
    ...


@main.command()
@click.option(
    "--path",
    type=click.Path(
        exists=False,
        file_okay=False,
        resolve_path=True,
        path_type=Path,
        writable=True,
    ),
    default="./",
    prompt="Path to initalize to",
)
@click.option(
    "--type",
    help="File type to initalize.",
    default="toml",
    type=click.Choice(("toml", "json", "py")),
    prompt="Configuration type",
)
def init(path: Path, type: str):
    from .config import JSON_BASE, PY_BASE, TOML_BASE

    fname = (
        "view.toml"
        if type == "toml"
        else "view.json"
        if type == "json"
        else "view_config.py"
    )
    if not path.exists():
        path.mkdir()

    conf_path = path / fname
    should_continue(f"`{conf_path}` already exists, overwrite?")

    with open(conf_path, "w") as f:
        f.write(
            TOML_BASE
            if type == "toml"
            else JSON_BASE
            if type == "json"
            else PY_BASE
        )

    click.echo(f"Created `{fname}`")

    app_path = path / "app.py"

    should_continue(f"`{app_path}` already exists, overwrite?")

    from .__about__ import __version__

    with open(app_path, "w") as f:
        f.write(
            f"# view.py {__version__}"
            """
import view


app = view.new_app()
app.run()
"""
        )

    click.echo("Created `app.py`")
    success(f"Successfully initalized app in `{path}`")
    return


if __name__ == "__main__":
    main()
