from typing import NoReturn

from rich.console import Console

_CONSOLE = Console()


def fatal_error(msg: str | None = None) -> NoReturn:
    _CONSOLE.print_exception()
    if msg:
        _CONSOLE.print(f"[bold red]Fatal Error[/bold red]: {msg}")
    _CONSOLE.print(
        "[bold red]Please report this on the [link=https://github.com/ZeroIntensity/view.py]issues tab[/link][/]"
    )
    exit(1)
