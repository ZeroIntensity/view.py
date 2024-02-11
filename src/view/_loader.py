from __future__ import annotations

import os
import sys
import warnings
from dataclasses import _MISSING_TYPE, Field, dataclass
from pathlib import Path
from typing import (TYPE_CHECKING, ForwardRef, Iterable, NamedTuple, TypedDict,
                    get_args, get_type_hints)

from _view import Context

from ._util import needs_dep, run_path

if not TYPE_CHECKING:
    from typing import _eval_type
else:

    def _eval_type(*args) -> Any:
        ...


import inspect

from ._logging import Internal
from ._util import docs_hint, is_annotated, is_union, set_load
from .exceptions import (DuplicateRouteError, InvalidBodyError,
                         InvalidRouteError, LoaderWarning)
from .routing import (BodyParam, Method, Route, RouteData, RouteInput,
                      _NoDefault)
from .typing import Any, RouteInputDict, TypeInfo, ValueType

ExtNotRequired = None
try:
    from typing import NotRequired  # type: ignore
except ImportError:
    NotRequired = None
    from typing_extensions import NotRequired as ExtNotRequired

from typing_extensions import get_origin

_NOT_REQUIRED_TYPES = []

if ExtNotRequired:
    _NOT_REQUIRED_TYPES.append(ExtNotRequired)

if NotRequired:
    _NOT_REQUIRED_TYPES.append(NotRequired)

if TYPE_CHECKING:
    from attrs import Attribute
    from pydantic.fields import ModelField

    from .app import App as ViewApp

    _TypedDictMeta = None
else:
    from typing import _TypedDictMeta

__all__ = "load_fs", "load_simple", "finalize"


TYPECODE_ANY = 0
TYPECODE_STR = 1
TYPECODE_INT = 2
TYPECODE_BOOL = 3
TYPECODE_FLOAT = 4
TYPECODE_DICT = 5
TYPECODE_NONE = 6
TYPECODE_CLASS = 7
TYPECODE_CLASSTYPES = 8
TYPECODE_LIST = 9


_BASIC_CODES = {
    str: TYPECODE_STR,
    int: TYPECODE_INT,
    bool: TYPECODE_BOOL,
    float: TYPECODE_FLOAT,
    dict: TYPECODE_DICT,
    None: TYPECODE_NONE,
    Any: TYPECODE_ANY,
    list: TYPECODE_LIST,
}

"""
Type info should contain up to four things:
    - Type Code
    - Type Object (only set when using a __view_body__ object)
    - Children (i.e. the `int` part of dict[str, int])
    - Default (only set when typecode is TYPECODE_CLASSTYPES)

This can be formatted as so:
    [(union1_tc, None, []), (union2_tc, None, [(type_tc, obj, [])])]
"""

"""
-- Route Data Information --
1 - Context
2 - WebSocket
"""


class _ViewNotRequired:
    __VIEW_NOREQ__ = 1


def _format_body(
    vbody_types: dict,
    doc: dict[Any, LoaderDoc],
    origin: type[Any],
    *,
    not_required: set[str] | None = None,
) -> list[TypeInfo]:
    """Generate a type info list from view body types."""
    not_required = not_required or set()
    if not isinstance(vbody_types, dict):
        raise InvalidBodyError(
            f"__view_body__ should return a dict, not {type(vbody_types)}",  # noqa
        )

    vbody_final = {}
    vbody_defaults = {}

    for k, raw_v in vbody_types.items():
        if not isinstance(k, str):
            raise InvalidBodyError(
                f"all keys returned by __view_body__ should be strings, not {type(k)}"  # noqa
            )

        default = _NoDefault
        v = raw_v.types if isinstance(raw_v, BodyParam) else raw_v

        if isinstance(v, str):
            scope = getattr(origin, "_view_scope", globals())
            v = _eval_type(ForwardRef(v), scope, scope)

        if isinstance(raw_v, BodyParam):
            default = raw_v.default

        if (getattr(raw_v, "__origin__", None) in _NOT_REQUIRED_TYPES) or (
            k in not_required
        ):
            v = get_args(raw_v)
            default = _ViewNotRequired
        iter_v = v if isinstance(v, (tuple, list)) else (v,)
        vbody_final[k] = _build_type_codes(
            iter_v,
            doc,
            key_name=k,
            default=default,
        )
        vbody_defaults[k] = default

    return [
        (TYPECODE_CLASSTYPES, k, v, vbody_defaults[k])
        for k, v in vbody_final.items()
    ]


@dataclass
class LoaderDoc:
    desc: str
    tp: Any
    default: Any


class _NotSet:
    """Sentinel value for default being not set in _build_type_codes."""

    ...


def _build_type_codes(
    inp: Iterable[type[ValueType]],
    doc: dict[Any, LoaderDoc] | None = None,
    *,
    key_name: str | None = None,
    default: Any | _NoDefault = _NotSet,
) -> list[TypeInfo]:
    """Generate types from a list of types.

    Args:
        inp: Iterable containing each type.
        doc: Auto-doc dictionary when a docstring is extracted.
        key_name: Name of the current key. Only needed for auto-doc purposes.
        default: Default value. Only needed for auto-doc purposes."""
    if not inp:
        return []

    codes: list[TypeInfo] = []

    for tp in inp:
        if is_annotated(tp):
            if doc is None:
                raise InvalidBodyError(f"Annotated is not valid here ({tp})")

            if not key_name:
                raise RuntimeError("internal error: key_name is None")

            if default is _NotSet:
                raise RuntimeError("internal error: default is _NotSet")

            tmp = tp.__origin__
            doc[key_name] = LoaderDoc(tp.__metadata__[0], tmp, default)
            tp = tmp
        elif doc is not None:
            if not key_name:
                raise RuntimeError("internal error: key_name is None")

            if default is _NotSet:
                raise RuntimeError("internal error: default is _NotSet")

            doc[key_name] = LoaderDoc("No description provided.", tp, default)

        type_code = _BASIC_CODES.get(tp)

        if type_code:
            codes.append((type_code, None, []))
            continue

        if (TypedDict in getattr(tp, "__orig_bases__", [])) or (
            type(tp) == _TypedDictMeta
        ):
            try:
                body = get_type_hints(tp)
            except KeyError:
                body = tp.__annotations__

            opt = getattr(tp, "__optional_keys__", None)

            class _Transport:
                @staticmethod
                def __view_construct__(**kwargs):
                    return kwargs

            doc = {}
            codes.append(
                (
                    TYPECODE_CLASS,
                    _Transport,
                    _format_body(body, doc, tp, not_required=opt),
                ),
            )
            setattr(tp, "_view_doc", doc)
            continue

        if (NamedTuple in getattr(tp, "__orig_bases__", [])) or (
            hasattr(tp, "_field_defaults")
        ):
            defaults = tp._field_defaults  # type: ignore
            tps = {}
            try:
                hints = get_type_hints(tp)
            except KeyError:
                hints = getattr(tp, "_field_types", tp.__annotations__)

            for k, v in hints.items():
                if k in defaults:
                    tps[k] = BodyParam(v, defaults[k])
                else:
                    tps[k] = v

            doc = {}
            codes.append((TYPECODE_CLASS, tp, _format_body(tps, doc, tp)))
            setattr(tp, "_view_doc", doc)
            continue

        dataclass_fields: dict[str, Field] | None = getattr(
            tp, "__dataclass_fields__", None
        )

        if dataclass_fields:
            tps = {}
            for k, v in dataclass_fields.items():
                if isinstance(v.default, _MISSING_TYPE) and (
                    isinstance(v.default_factory, _MISSING_TYPE)
                ):
                    tps[k] = v.type
                else:
                    default = (
                        v.default
                        if not isinstance(v.default, _MISSING_TYPE)
                        else v.default_factory
                    )
                    tps[k] = BodyParam(v.type, default)

            doc = {}
            codes.append((TYPECODE_CLASS, tp, _format_body(tps, doc, tp)))
            setattr(tp, "_view_doc", doc)
            continue

        pydantic_fields: dict[str, ModelField] | None = getattr(
            tp, "__fields__", None
        ) or getattr(tp, "model_fields", None)
        if pydantic_fields:
            tps = {}

            for k, v in pydantic_fields.items():
                if (not v.default) and (not v.default_factory):
                    tps[k] = v.outer_type_  # type: ignore
                else:
                    tps[k] = BodyParam(
                        v.outer_type_,  # type: ignore
                        v.default or v.default_factory,
                    )

            doc = {}
            codes.append((TYPECODE_CLASS, tp, _format_body(tps, doc, tp)))
            setattr(tp, "_view_doc", doc)
            continue

        attrs_fields: tuple[Attribute, ...] | None = getattr(
            tp, "__attrs_attrs__", None
        )
        if attrs_fields:
            try:
                from attrs import Factory
            except ModuleNotFoundError as e:
                needs_dep("attrs", e)

            tps = {}

            for i in attrs_fields:
                default = i.default
                if not default:
                    tps[i.name] = i.type
                else:
                    tps[i.name] = BodyParam(
                        i.type,  # type: ignore
                        default.factory if isinstance(default, Factory) else default,  # type: ignore
                    )

            doc = {}
            codes.append((TYPECODE_CLASS, tp, _format_body(tps, doc, tp)))
            setattr(tp, "_view_doc", doc)
            continue

        vbody = getattr(tp, "__view_body__", None)
        if vbody:
            if callable(vbody):
                vbody_types = vbody()
            else:
                vbody_types = vbody

            doc = {}
            codes.append(
                (TYPECODE_CLASS, tp, _format_body(vbody_types, doc, tp))
            )
            setattr(tp, "_view_doc", doc)
            continue

        origin = get_origin(tp)
        if is_union(type(tp)) and (origin not in {dict, list}):
            new_codes = _build_type_codes(get_args(tp))
            codes.extend(new_codes)
            continue

        if origin is dict:
            key, value = get_args(tp)

            if key is not str:
                raise InvalidBodyError(
                    f"dictionary keys must be strings, not {key}"
                )

            tp_codes = _build_type_codes((value,))
            codes.append((TYPECODE_DICT, None, tp_codes))
        elif origin is list:
            tps = get_args(tp)
            codes.append((TYPECODE_LIST, None, _build_type_codes(tps)))
        else:
            raise InvalidBodyError(f"{tp} is not a valid type for routes")

    return codes


def _format_inputs(
    inputs: list[RouteInput | RouteData],
) -> list[RouteInputDict | RouteData]:
    """Convert a list of route inputs to a proper dictionary that the C loader can handle.
    This function also will generate the typecodes for the input."""
    result: list[RouteInputDict | RouteData] = []

    for i in inputs:
        if not isinstance(i, RouteInput):
            result.append(i)
            continue
        type_codes = _build_type_codes(i.tp)
        Internal.info("built type codes:", type_codes)
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
    """Attach list of routes to an app and validate all parameters.

    Args:
        routes: List of routes.
        app: App to attach to.
    """
    virtual_routes: dict[str, list[Route]] = {}

    targets = {
        Method.GET: app._get,
        Method.POST: app._post,
        Method.PUT: app._put,
        Method.PATCH: app._patch,
        Method.DELETE: app._delete,
        Method.OPTIONS: app._options,
        Method.WEBSOCKET: app._websocket,
    }

    for route in routes:
        set_load(route)

        if route.method:
            target = targets[route.method]
        else:
            target = None

        if (not route.path) and (not route.parts):
            raise InvalidRouteError(f"{route} did not specify a path")
        lst = virtual_routes.get(route.path or "")

        if lst:
            if route.method in [i.method for i in lst]:
                assert route.method
                raise DuplicateRouteError(
                    f"duplicate route: {route.method.name} for {route.path}",
                )
            lst.append(route)
        else:
            virtual_routes[route.path or ""] = [route]

        sig = inspect.signature(route.func)
        route.inputs = [i for i in reversed(route.inputs)]

        if len(sig.parameters) != len(route.inputs):
            names = [i.name for i in route.inputs if isinstance(i, RouteInput)]
            index = 0

            for k, v in sig.parameters.items():
                if k in names:
                    index += 1
                    continue

                tp = v.annotation if v.annotation is not inspect._empty else Any

                if tp is Context:
                    route.inputs.insert(index, 1)
                    continue

                default = (
                    v.default if v.default is not inspect._empty else _NoDefault
                )

                route.inputs.insert(
                    index,
                    RouteInput(
                        k,
                        False,
                        (tp,),
                        default,
                        None,
                        [],
                    ),
                )
                index += 1

            if len(route.inputs) != len(sig.parameters):
                raise InvalidRouteError(
                    "mismatch in parameter names with automatic route inputs",
                    hint=docs_hint(
                        "https://view.zintensity.dev/building-projects/parameters/#automatically"
                    ),
                )

        app.loaded_routes.append(route)
        if target:
            target(
                route.path,  # type: ignore
                route.func,
                route.cache_rate,
                _format_inputs(route.inputs),
                route.errors or {},
                route.parts,  # type: ignore
                [i for i in reversed(route.middleware_funcs)],
            )
        else:
            for i in (route.method_list) or targets.keys():
                target = targets[i]
                target(
                    route.path,  # type: ignore
                    route.func,
                    route.cache_rate,
                    _format_inputs(route.inputs),
                    route.errors or {},
                    route.parts,  # type: ignore
                    [i for i in reversed(route.middleware_funcs)],
                )


def load_fs(app: ViewApp, target_dir: Path) -> None:
    """Filesystem loading implementation.
    Similiar to NextJS's routing system. You take `target_dir` and search it,
    if a file is found and not prefixed with _, then convert the directory structure
    to a path. For example, target_dir/hello/world/index.py would be converted to a
    route for /hello/world

    Args:
        app: App to attach routes to.
        target_dir: Directory to search for routes.
    """
    Internal.info("loading using filesystem")
    Internal.debug(f"loading {app}")

    routes: list[Route] = []

    if not target_dir.exists():
        raise FileNotFoundError(f"{target_dir.absolute()} does not exist")

    sys.path.append(str(target_dir.absolute()))
    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.startswith("_"):
                continue

            path = os.path.join(root, f)
            mod = run_path(path)
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
                raise InvalidRouteError(f"{path} has no set routes")

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
                    stripped_path = str(stripped_obj).rsplit(
                        ".",
                        maxsplit=1,
                    )[0]
                    x.path = "/" + stripped_path

            for x in current_routes:
                routes.append(x)

    finalize(routes, app)


def load_simple(app: ViewApp, target_dir: Path) -> None:
    """Simple loading implementation.
    Simple loading is essentially searching a directory recursively
    for files, and then extracting Route instances from each file.

    If a file is prefixed with _, it will not be loaded.

    Args:
        app: App to attach routes to.
        target_dir: Directory to search for routes.

    """
    Internal.info("loading using simple strategy")
    routes: list[Route] = []

    if not target_dir.exists():
        raise FileNotFoundError(f"{target_dir.absolute()} does not exist")

    sys.path.append(str(target_dir.absolute()))

    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.startswith("_"):
                continue

            path = os.path.join(root, f)
            mod = run_path(path)
            mini_routes: list[Route] = []

            for i in mod.values():
                if isinstance(i, Route):
                    mini_routes.append(i)

            for route in mini_routes:
                if not route.path:
                    raise InvalidRouteError(
                        "omitting path is only supported"
                        " on filesystem loading",
                    )

                routes.append(route)

    finalize(routes, app)


def load_patterns(app: ViewApp, target_path: Path) -> None:
    Internal.info("loading using patterns strategy")
    mod = run_path(str(target_path))
    patterns = (
        mod.get("PATTERNS")
        or mod.get("URL_PATTERNS")
        or mod.get("URLPATTERNS")
        or mod.get("urlpatterns")
        or mod.get("patterns")
        or mod.get("url_patterns")
    )

    if not patterns:
        raise InvalidRouteError(
            f"{target_path} did not define a PATTERNS, URL_PATTERNS, URLPATTERNS, urlpatterns, or patterns variable"
        )

    finalize(patterns, app)
