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
    """Base class for all warnings in view.py"""

    ...


class NotLoadedWarning(ViewWarning):
    """load() was never called"""

    ...


class LoaderWarning(ViewWarning):
    """A warning from the loader."""

    ...


class ViewError(Exception):
    """Base class for exceptions in view.py"""

    def __init__(
        self,
        *args: object,
        hint: RenderableType | None = None,
    ) -> None:
        self.hint = hint
        super().__init__(*args)


<<<<<<< HEAD
=======
class MissingLibraryError(ViewError):
    """A library is not installed."""

    ...


>>>>>>> 2ea7b03fcb51ac30d69cf27ca61c7ad6484c8bb4
class EnvironmentError(ViewError):
    """An environment variable is missing."""

    ...


class InvalidBodyError(ViewError):
    """The specified type cannot be used as a view body."""

    ...


class MistakeError(ViewError):
    """The user made a mistake."""

    ...


class AppNotFoundError(ViewError, FileNotFoundError):
    """Couldn't find the app from the given path."""

    ...
