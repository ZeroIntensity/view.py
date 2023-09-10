from __future__ import annotations

import os
import runpy
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, get_args

from ._logging import Internal
from ._util import set_load
from .exceptions import InvalidBodyError, LoaderWarning
from .routing import Method, Route, RouteInput, _NoDefault
from .typing import Any, RouteInputDict, TypeInfo, ValueType

if TYPE_CHECKING:
    from .app import ViewApp

__all__ = "load_fs", "load_simple", "finalize"


TYPECODE_ANY = 0
TYPECODE_STR = 1
TYPECODE_INT = 2
TYPECODE_BOOL = 3
TYPECODE_FLOAT = 4
TYPECODE_DICT = 5
TYPECODE_NONE = 6
TYPECODE_CLASS = 7


_BASIC_CODES = {
    str: TYPECODE_STR,
    int: TYPECODE_INT,
    bool: TYPECODE_BOOL,
    float: TYPECODE_FLOAT,
    dict: TYPECODE_DICT,
    None: TYPECODE_NONE,
    Any: TYPECODE_ANY,
}

"""
Type info should contain three things:
    - Type Code
    - Type Object (only set when using a __view_body__ object)
    - Children (i.e. the `int` part of dict[str, int])

This can be formatted as so:
    [(union1_tc, None, []), (union2_tc, None, [(type_tc, obj, [])])]
"""


def _build_type_codes(inp: Iterable[type[ValueType]]) -> list[TypeInfo]:
    if not inp:
        return []

    codes: list[TypeInfo] = []

    for tp in inp:
        type_code = _BASIC_CODES.get(tp)

        if type_code:
            codes.append((type_code, None, []))
            continue

        vbody = getattr(tp, "__view_body__", None)
        if vbody:
            raise NotImplementedError
            """
            if callable(vbody):
                vbody_types = vbody()
            else:
                vbody_types = vbody

            codes.append((TYPECODE_CLASS, tp, _build_type_codes(vbody_types)))
            """

        origin = getattr(tp, "__origin__", None)  # typing.GenericAlias

        if (not origin) and (origin is not dict):
            raise InvalidBodyError(f"{tp} is not a valid type for routes")

        key, value = get_args(tp)

        if key is not str:
            raise InvalidBodyError(
                f"dictionary keys must be strings, not {key}"
            )

        value_args = get_args(value)

        if not len(value_args):
            value_args = (value,)

        tp_codes = _build_type_codes(value_args)
        codes.append((TYPECODE_DICT, None, tp_codes))

    return codes


def _format_inputs(inputs: list[RouteInput]) -> list[RouteInputDict]:
    result: list[RouteInputDict] = []

    for i in inputs:
        type_codes = _build_type_codes(i.tp)

        result.append(
            {
                "name": i.name,
                "type_codes": type_codes,
                "default": i.default,  # type: ignore
                "validators": i.validators,
                "is_body": i.is_body,
                "has_default": i.default is not _NoDefault,
            }
        )

    return result


def finalize(routes: list[Route], app: ViewApp):
    virtual_routes: dict[str, list[Route]] = {}

    targets = {
        Method.GET: app._get,
        Method.PATCH: app._post,
        Method.PUT: app._put,
        Method.PATCH: app._patch,
        Method.DELETE: app._delete,
        Method.OPTIONS: app._options,
    }

    for route in routes:
        set_load(route)
        target = targets[route.method]

        if (not route.path) and (not route.parts):
            raise TypeError("route did not specify a path")
        lst = virtual_routes.get(route.path or "")

        if lst:
            if route.method in [i.method for i in lst]:
                raise ValueError(
                    f"duplicate route: {route.method.name} for {route.path}",
                )
            lst.append(route)
        else:
            virtual_routes[route.path or ""] = [route]

        target(
            route.path,  # type: ignore
            route.callable,
            route.cache_rate,
            _format_inputs(route.inputs),
            route.errors or {},
            route.parts,  # type: ignore
        )


def load_fs(app: ViewApp, target_dir: Path):
    Internal.info("loading using filesystem")
    Internal.debug(f"loading {app}")

    routes: list[Route] = []

    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.startswith("_"):
                continue

            path = os.path.join(root, f)
            Internal.info(f"loading: {path}")
            mod = runpy.run_path(path)
            current_routes: list[Route] = []

            for i in mod.values():
                if isinstance(i, Route):
                    if i.method in [x.method for x in current_routes]:
                        warnings.warn(
                            "same method used twice during filesystem loading",
                            LoaderWarning,
                        )
                    current_routes.append(i)

            if not current_routes:
                raise ValueError(f"{path} has no set routes")

            for x in current_routes:
                if x.path:
                    warnings.warn(
                        f"path was passed for {x} when filesystem loading is enabled"  # noqa
                    )
                else:
                    path_obj = Path(path)
                    stripped = list(
                        path_obj.parts[len(target_dir.parts) :]
                    )  # noqa
                    if stripped[-1] == "index.py":
                        stripped.pop(len(stripped) - 1)

                    stripped_obj = Path(*stripped)
                    stripped_path = str(stripped_obj).rsplit(".", maxsplit=1)[0]
                    x.path = "/" + stripped_path

            for x in current_routes:
                routes.append(x)

    finalize(routes, app)


def load_simple(app: ViewApp, target_dir: Path):
    Internal.info("loading using simple strategy")
    routes: list[Route] = []

    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.startswith("_"):
                continue

            path = os.path.join(root, f)
            Internal.info(f"loading: {path}")
            mod = runpy.run_path(path)
            mini_routes: list[Route] = []

            for i in mod.values():
                if isinstance(i, Route):
                    mini_routes.append(i)

            for route in mini_routes:
                if not route.path:
                    raise ValueError(
                        "omitting path is only supported"
                        " on filesystem loading",
                    )

                routes.append(route)

    finalize(routes, app)
