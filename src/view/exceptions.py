from __future__ import annotations

from rich.console import RenderableType

__all__ = (
    "ViewWarning",
    "NotLoadedWarning",
    "ViewError",
    "MissingLibraryError",
    "BadEnvironmentError",
    "InvalidBodyError",
    "MistakeError",
    "LoaderWarning",
    "AppNotFoundError",
    "DuplicateRouteError",
    "InvalidRouteError",
    "ViewInternalError",
    "ConfigurationError",
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


class MissingLibraryError(ViewError):
    """A library is not installed."""

    ...


class BadEnvironmentError(ViewError):
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


class DuplicateRouteError(ViewError):
    """Duplicate routes in loader."""

    ...


class InvalidRouteError(ViewError):
    """Something is wrong with a route."""

    ...


class ViewInternalError(ViewError):
    """Something was wrong internally."""

    ...


class ConfigurationError(ViewError):
    """Something is wrong with the configuration."""

    ...
