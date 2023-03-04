from __future__ import annotations

import inspect
import json
import os
import re
import runpy
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generic, Literal, TypeVar

import toml

from .__about__ import __version__

__all__ = "Config", "config", "load_config", "load_dict"

JsonValue = str | int | bool | float | dict[str | int, "JsonValue"]

FINDER_REGEX = re.compile(r"([a-z]+((\d)|([A-Z0-9][a-z0-9]+))*([A-Z])?)\Z")
CONVERTER_REGEX = re.compile(r"(?<!^)(?=[A-Z])")


def _switch_case(data: str) -> str:
    return CONVERTER_REGEX.sub("_", data).lower()


def _convert(data: dict) -> dict:
    new = data.copy()

    for i in data:
        if isinstance(i, str):
            if FINDER_REGEX.match(i):
                new_name: str = _switch_case(i)
                new[new_name] = new.pop(i)

    return new


def config(obj: type[T]) -> type[T]:
    if not os.environ.get("_VIEW_CFG"):
        raise RuntimeError("attempted to execute view config file")

    # NOTE: we need to access the globals from the frame
    # due to python not reloading the globals() in this
    # function
    cframe = inspect.currentframe()
    assert cframe, "failed to acquire frame"

    frame = cframe.f_back
    assert frame, "frame has no f_back"

    try:
        _config: Callable[[type], type] = frame.f_globals["_config"]
    except KeyError as e:
        raise RuntimeError("_VIEW_CFG set without defining _config") from e

    _config(obj)
    return obj


TOML_BASE = f"""# view.py {__version__}
[network]

[app]

[env]
"""

JSON_BASE = """{
    "network": {},
    "app": {},
    "env": {}
}"""

PY_BASE = (
    f"# view.py {__version__}"
    """
from __future__ import annotations
from view.config import config, NetworkConfig, AppConfig


@config
class Config:
    network = NetworkConfig()
    app = AppConfig()
    env: dict[str, str] = {}
"""
)


@dataclass()
class AppConfig:
    load_strategy: str = "manual"
    server: str = "uvicorn"
    dev: bool = True
    path: str = "app.py:app"
    use_uvloop: Literal["decide"] | bool = "decide"


@dataclass()
class NetworkConfig:
    port: int = 5000
    host: str = "0.0.0.0"
    extra_args: dict[str, JsonValue] = field(default_factory=dict)
    change_port_prod: bool = True


class Config:
    def _calculate_difference(
        self, values: dict[Any, Any] | None, tp: type
    ) -> None:
        if not values:
            return

        for k in values:
            if k not in tp.__annotations__:
                raise ValueError(f"invalid key for {tp.__name__}: {k}")

    def __init__(
        self,
        network: dict[Any, Any] | None = None,
        app: dict[Any, Any] | None = None,
        env: dict[str, str] | None = None,
    ):
        self._calculate_difference(network, NetworkConfig)
        self.network = NetworkConfig(**(network or {}))
        self._calculate_difference(app, AppConfig)
        self.app = AppConfig(**(app or {}))
        self.env = env or {}


CONFIG_TARGETS = ("view.toml", "view.json", "view_config.py")


def _ob_dict(ob: object) -> dict:
    d = {k: v for k, v in vars(ob).items() if not k.startswith("__")}

    for k, v in d.items():
        if hasattr(v, "__dict__"):
            d[k] = _ob_dict(v)

    return d


def _load_path(path: Path) -> dict:
    if path.suffix == ".toml":
        return toml.loads(path.read_text())
    if path.suffix == ".json":
        return json.loads(path.read_text())
    if path.suffix == ".py":
        ob: type | None = None

        def conf_wrapper(obj: type):
            nonlocal ob
            ob = obj

        os.environ["_VIEW_CFG"] = "1"
        runpy.run_path(str(path), {"_config": conf_wrapper})
        del os.environ["_VIEW_CFG"]

        if not ob:
            raise TypeError("config wasnt set")
        return _ob_dict(ob)
    raise ValueError(f"cannot load {path}")


T = TypeVar("T")
Loader = Callable[[JsonValue], T]


@dataclass()
class _Validator(Generic[T]):
    type: type[T]
    is_of: set[str] | None = None
    loader: Loader[T] | None = None


def _int_loader(value: JsonValue) -> int:
    try:
        if isinstance(value, dict):
            raise ValueError
        return int(value)
    except ValueError:
        raise TypeError(f"{value!r} is not int-like") from None


def _bool_loader(value: JsonValue) -> bool:
    if isinstance(value, (bool, int)):
        return bool(value)

    raise TypeError(f"expected bool, got {value!r}")


def _use_uvloop_loader(value: JsonValue) -> bool:
    if isinstance(value, (bool, str)):
        if isinstance(value, str):
            if value != "decide":
                raise TypeError("must be true, false, or 'decide'")
            else:
                try:
                    import uvloop  # noqa

                    return True
                except ImportError:
                    return False

        return value

    raise TypeError(f"expected bool, got {value}")


def _extra_args_loader(value: JsonValue) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise TypeError(f"expected a key-value mapping (dict), got {value!r}")

    for k in value:
        if not isinstance(k, str):
            raise TypeError(f"all keys must be a string ({k!r} is not)")

    return value  # type: ignore


_CONFIG_VALIDATORS: dict[str, _Validator] = {
    "server": _Validator(str, is_of={"view", "uvicorn", "hypercorn"}),
    "load_strategy": _Validator(str, is_of={"manual", "auto", "simple"}),
    "use_uvloop": _Validator(bool, loader=_use_uvloop_loader),
    "extra_args": _Validator(dict, loader=_extra_args_loader),
}

_ANNOTATIONS: dict[str, Loader] = {"int": _int_loader, "bool": _bool_loader}
# annotations are converted to strings due to future import


def _validate_config(config: Any) -> None:
    for k, validator in _CONFIG_VALIDATORS.items():
        attr = getattr(config, k, None)
        if attr is None:  # in case false was passed
            continue

        if validator.loader:
            try:
                attr = validator.loader(attr)
            except TypeError as e:
                raise ValueError(f"error for config key {k!r}: {e}") from None

        if not isinstance(attr, validator.type):
            raise TypeError(
                f"wrong type for config key {k!r}: expected"
                f"{validator.type.__name__}, got {type(attr).__name__}"
            )

        values = validator.is_of
        if values:
            if attr not in values:
                raise ValueError(
                    f"invalid value for config key {k!r}:"
                    f"expected one of {', '.join(values)}, got {attr}"
                )

    for k, tp in type(config).__annotations__.items():
        loader = _ANNOTATIONS.get(tp)
        if loader:
            try:
                setattr(config, k, loader(getattr(config, k)))
            except TypeError as e:
                raise ValueError(f"error for config key {k!r}: {e}") from None


def load_dict(obj: dict[Any, Any]) -> Config:
    for k in obj:
        if k not in inspect.signature(Config.__init__).parameters:
            raise ValueError(f"invalid key for config: {k}")
    result = Config(**obj)
    _validate_config(result.app)
    _validate_config(result.network)

    for k, v in result.env.values():
        os.environ[k] = v

    return result


def load_config(
    path: str | Path | None = None,
    overrides: dict | None = None,
    *,
    default: bool = False,
) -> Config:
    p: Path | None = None

    if not path:
        parent = Path().parent.absolute()

        for target in CONFIG_TARGETS:
            tmp = Path(os.path.join(parent, target))
            if tmp.exists():
                p = tmp
                break
        if not p:
            if not default:
                raise TypeError(f"no config found in {parent}")
            else:
                return Config()
    else:
        p = path if not isinstance(path, str) else Path(path)
        if not p.exists():
            raise FileNotFoundError(f"{p.absolute()} does not exist")

    conf = _load_path(p)
    conf.update(overrides or {})
    return load_dict(_convert(conf))
