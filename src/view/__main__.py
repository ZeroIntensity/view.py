import os
from pathlib import Path

import click


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
        exists=True,
        file_okay=False,
        resolve_path=True,
        path_type=Path,
        writable=True,
    ),
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
        with open(path / fname, "w") as f:
            f.write(
                TOML_BASE
                if type == "toml"
                else JSON_BASE
                if type == "json"
                else PY_BASE
            )

        click.echo(f"Created `{fname}`")

        with open(path / "app.py", "w") as f:
            f.write(
                """from view import new_app

app = new_app()
app.run()"""
            )

        click.echo(f"Created `{path / 'app.py'}`")
        click.secho(f"Successfully initalized app in `{path}`", fg="green")
        return

    if operation == "serve":
        from .config import load_config
        from .util import run as run_mod

        os.environ["_VIEW_RUN"] = "1"

        conf = load_config()
        run_mod(conf.app.path)


if __name__ == "__main__":
    main()
