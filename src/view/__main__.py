import os
from pathlib import Path

import click

from .__about__ import __version__


def success(msg: str) -> None:
    click.secho(msg, fg="green", bold=True)


def warn(msg: str) -> None:
    click.secho(msg, fg="yellow", bold=True)


def error(msg: str) -> None:
    click.secho(msg, fg="red", bold=True)
    exit(-1)


@click.command()
@click.argument("operation", type=click.Choice(("init", "serve")))
@click.option(
    "--type",
    help="File type to initalize.",
    default="toml",
    type=click.Choice(("toml", "json", "py")),
)
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
)
def main(operation: str, type: str, path: Path):
    if operation == "init":
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
        if conf_path.exists():
            if not click.confirm(
                click.style(
                    f"`{conf_path}` already exists, overwrite?", fg="yellow"
                )
            ):
                exit(-1)

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

        if app_path.exists():
            if not click.confirm(
                click.style(
                    f"`{app_path}` already exists, overwrite?", fg="yellow"
                )
            ):
                exit(-1)

        with open(app_path, "w") as f:
            f.write(
                f"# view.py {__version__}"
                """
from view import new_app


app = new_app()
app.run()"""
            )

        click.echo("Created `app.py`")
        success(f"Successfully initalized app in `{path}`")
        return

    if operation == "serve":
        from .config import load_config
        from .util import run as run_path

        os.environ["_VIEW_RUN"] = "1"

        conf = load_config()
        run_path(conf.app.path)


if __name__ == "__main__":
    main()
