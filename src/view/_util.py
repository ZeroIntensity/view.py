import importlib
from types import ModuleType as Module
from typing import get_type_hints

from .typing import ViewBody, ViewBodyLike


def attempt_import(name: str, *, repr_name: str | None = None) -> Module:
    try:
        return importlib.import_module(name)
    except ImportError as e:
        raise ValueError(
            f"{repr_name or name} is not installed! (`pip install {name}`)"
        ) from e


def get_body(tp: ViewBodyLike) -> ViewBody:
    body_attr: ViewBody | None = getattr(tp, "__view_body__", None)

    if body_attr:
        if callable(body_attr):
            return body_attr()

        assert isinstance(body_attr, dict), "__view_body__ is not a dict"
        return body_attr

    return get_type_hints(tp)
