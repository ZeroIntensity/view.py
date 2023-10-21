from __future__ import annotations

from rich.console import RenderableType

__all__ = (
    "ViewWarning",
    "NotLoadedWarning",
    "ViewError",
    "EnvironmentError",
    "InvalidBodyError",
    "MistakeError",
    "LoaderWarning",
    "AppNotFoundError",
)


class ViewWarning(UserWarning):
    ...


class NotLoadedWarning(ViewWarning):
    ...


class LoaderWarning(ViewWarning):
    ...


class ViewError(Exception):
    def __init__(
        self,
        *args: object,
        hint: RenderableType | None = None,
    ) -> None:
        self.hint = hint
        super().__init__(*args)


class EnvironmentError(ViewError):
    ...


class InvalidBodyError(ViewError):
    ...


class MistakeError(ViewError):
    ...


class AppNotFoundError(ViewError, FileNotFoundError):
    ...
