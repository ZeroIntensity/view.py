from __future__ import annotations

import importlib.util
import sys
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any, Dict, Literal, Union

from configzen import ConfigField, ConfigModel


class AppConfig(ConfigModel):
    loader: Literal["manual", "simple", "filesystem"] = "manual"
    app_path: str = ConfigField("app.py:app")
    uvloop: Union[Literal["decide"], bool] = "decide"
    loader_path: Path = Path("./routes")


class ServerConfig(ConfigModel):
    host: IPv4Address = IPv4Address("0.0.0.0")
    port: int = 5000
    backend: Literal["uvicorn"] = "uvicorn"
    extra_args: Dict[str, Any] = ConfigField(default_factory=dict)


class LogConfig(ConfigModel):
    level: Union[
        Literal["debug", "info", "warning", "error", "critical"], int
    ] = "info"
    hijack: bool = True
    fancy: bool = True
    pretty_tracebacks: bool = True


class Config(ConfigModel):
    dev: bool = True
    app: AppConfig = ConfigField(default_factory=AppConfig)
    server: ServerConfig = ConfigField(default_factory=ServerConfig)
    log: LogConfig = ConfigField(default_factory=LogConfig)


B_OPEN = "{"
B_CLOSE = "}"
B_OC = "{}"


def make_preset(tp: str, loader: str) -> str:
    if tp == "toml":
        return f"""dev = true

[app]
loader = "{loader}"

[server]

[log]
"""
    if tp == "json":
        return f"""{B_OPEN}
    "dev": true,
    "app": {B_OPEN}
        "loader": "{loader}"
    {B_CLOSE}
    "server": {B_OC},
    "log": {B_OC}
{B_CLOSE}"""

    if tp == "ini":
        return f"""dev = 'true'

[app]
loader = {loader}

[server]

[log]
"""

    if tp in {"yml", "yaml"}:
        return f"""
app:
    loader: "{loader}"
"""

    if tp == "py":
        return f"""dev = True

app = {B_OPEN}
    "loader": "{loader}"
{B_CLOSE}

server = {B_OC}
log = {B_OC}"""

    raise ValueError("bad file type")


def load_config(
    path: Path | None = None,
    *,
    directory: Path | None = None,
) -> Config:
    paths = (
        "view.toml",
        "view.json",
        "view.ini",
        "view.yaml",
        "view.yml",
        "view_config.py",
        "config.py",
    )

    if path:
        if directory:
            return Config.load(directory / path)
            # idk why someone would do this, but i guess its good to support it
        return Config.load(path)

    for i in paths:
        p = Path(i) if not directory else directory / i

        if not p.exists():
            continue

        if p.suffix == ".py":
            spec = importlib.util.spec_from_file_location(str(p))
            assert spec, "spec is none"
            mod = importlib.util.module_from_spec(spec)
            assert mod, "mod is none"
            sys.modules[p.stem] = mod
            assert spec.loader, "spec.loader is none"
            spec.loader.exec_module(mod)
            return Config.wrap_module(mod)

        return Config.load(p)

    return Config()
