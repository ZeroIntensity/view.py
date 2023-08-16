from ipaddress import IPv4Address
from pathlib import Path
from typing import Any, Literal

from configzen import ConfigField, ConfigModel


class AppConfig(ConfigModel):
    loader: Literal["manual", "simple", "filesystem"] = "manual"
    app_path: str = ConfigField("app.py:app")
    uvloop: Literal["decide"] | bool = "decide"
    loader_path: Path = Path("./routes")


class ServerConfig(ConfigModel):
    host: IPv4Address = IPv4Address("0.0.0.0")
    port: int = 5000
    backend: Literal["uvicorn", "hypercorn"] = "uvicorn"
    extra_args: dict[str, Any] = ConfigField(default_factory=dict)


class LogConfig(ConfigModel):
    level: Literal[
        "debug", "info", "warning", "error", "critical"
    ] | int = "info"
    hijack: bool = True
    fancy: bool = True
    pretty_tracebacks: bool = True


class Config(ConfigModel):
    dev: bool = True
    app: AppConfig = ConfigField(default_factory=AppConfig)
    server: ServerConfig = ConfigField(default_factory=ServerConfig)
    log: LogConfig = ConfigField(default_factory=LogConfig)


def make_preset(tp: str, loader: str):
    if tp == "toml":
        return f"""dev = true

[app]
loader = "{loader}"

[server]

[log]
"""
    if tp == "json":
        return (
            '''{
    "dev": true,
    "app": {
        "loader": "'''
            + loader
            + """"
    },
    "server": {},
    "log": {}
}"""
        )

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

    raise ValueError("bad type")


def load_config() -> Config:
    paths = (
        "view.toml",
        "view.json",
        "view.ini",
        "view.yaml",
        "view.yml",
    )

    for i in paths:
        p = Path(i)
        if p.exists():
            return Config.load(p)

    return Config()
