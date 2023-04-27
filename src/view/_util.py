import importlib
import warnings
import weakref
from types import ModuleType as Module
from typing import get_type_hints

from .exceptions import InvalidBodyError, MissingLibraryError, NotLoadedWarning
from .typing import Any, ViewBody, ViewBodyLike


class LoadChecker:
    def _view_load_check(self) -> None:
        if not self._view_loaded:
            warnings.warn(f"{self} was never loaded", NotLoadedWarning)

    def __init__(self) -> None:
        self._view_loaded = False
        weakref.finalize(self, self._view_load_check)


def set_load(cl: LoadChecker):
    """Let the developer feel that they aren't touching private members."""
    cl._view_loaded = True


def attempt_import(name: str, *, repr_name: str | None = None) -> Module:
    try:
        return importlib.import_module(name)
    except ImportError as e:
        raise MissingLibraryError(
            f"{repr_name or name} is not installed! (`pip install {name}`)"
        ) from e


_VALID_BODY = {str, int, type, dict, float, bool}


def validate_body(body: ViewBody) -> None:
    for v in body.values():
        if v not in _VALID_BODY:
            raise InvalidBodyError(
                f"{type(v).__name__} is not a valid type for a body",
            )

        if isinstance(v, dict):
            validate_body(v)

        if isinstance(v, type):
            validate_body(get_body(v))


def get_body(tp: ViewBodyLike | Any) -> ViewBody:
    body_attr: ViewBody | None = getattr(tp, "__view_body__", None)

    if body_attr:
        if callable(body_attr):
            return body_attr()

        assert isinstance(body_attr, dict), "__view_body__ is not a dict"
        return body_attr

    return get_type_hints(tp)
