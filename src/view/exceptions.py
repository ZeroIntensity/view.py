class ViewWarning(UserWarning):
    ...


class NotLoadedWarning(ViewWarning):
    ...


class ViewError(Exception):
    ...


class MissingLibraryError(ViewError):
    ...


class EnvironmentError(ViewError):
    ...


class InvalidBodyError(ViewError):
    ...
