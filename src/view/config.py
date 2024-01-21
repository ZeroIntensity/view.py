from __future__ import annotations

import importlib.util
import sys
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any, Dict, Literal, Union

from configzen import ConfigField, ConfigModel, field_validator

from .exceptions import ViewInternalError
from .logging import FileWriteMethod, Urgency
from .typing import TemplateEngine

class AppConfig(ConfigModel, env_prefix="view_app_"):
    loader: Literal["manual", "simple", "filesystem", "patterns"] = "manual"
    app_path: str = ConfigField("app.py:app")
    uvloop: Union[Literal["decide"], bool] = "decide"
    loader_path: Path = Path("./routes")

    @field_validator("loader")
    @classmethod
    def validate_loader(cls, loader: str):
        return loader

    @field_validator("loader_path")
    @classmethod
    def validate_loader_path(cls, loader_path: Path, values: dict):
        loader = values["loader"]
        if loader == "manual":
            return loader_path

        if (loader == "patterns") and (loader_path == Path("./routes")):
            return Path("./urls.py").resolve()

        return loader_path.resolve()


class ServerConfig(ConfigModel, env_prefix="view_server_"):
    host: IPv4Address = IPv4Address("0.0.0.0")
    port: int = 5000
    backend: Literal["uvicorn"] = "uvicorn"
    extra_args: Dict[str, Any] = ConfigField(default_factory=dict)


class UserLogConfig(ConfigModel, env_prefix="view_user_log_"):
    urgency: Urgency = "info"
    log_file: Union[Path, str, None] = None
    show_time: bool = True
    show_caller: bool = True
    show_color: bool = True
    show_urgency: bool = True
    file_write: FileWriteMethod = "both"
    strftime: str = "%H:%M:%S"


class LogConfig(ConfigModel, env_prefix="view_log_"):
    level: Union[
        Literal["debug", "info", "warning", "error", "critical"], int
    ] = "info"
    hijack: bool = True
    fancy: bool = True
    pretty_tracebacks: bool = True
    user: UserLogConfig = ConfigField(default_factory=UserLogConfig)


class MongoConfig(ConfigModel, env_prefix="view_mongo_"):
    host: IPv4Address
    port: int
    username: str
    password: str
    database: str


class PostgresConfig(ConfigModel, env_prefix="view_postgres_"):
    database: str
    user: str
    password: str
    host: IPv4Address
    port: int


class SQLiteConfig(ConfigModel, env_prefix="view_sqlite_"):
    file: Path


class MySQLConfig(ConfigModel, env_prefix="view_mysql_"):
    host: IPv4Address
    user: str
    password: str
    database: str


class DatabaseConfig(ConfigModel, env_prefix="view_database_"):
    type: Literal["sqlite", "mysql", "postgres", "mongo"] = "sqlite"
    mongo: Union[MongoConfig, None] = None
    postgres: Union[PostgresConfig, None] = None
    sqlite: Union[SQLiteConfig, None] = SQLiteConfig(file="view.db")
    mysql: Union[MySQLConfig, None] = None


class TemplatesConfig(ConfigModel, env_prefix="view_templates_"):
    directory: Path = Path("./templates")
    locals: bool = True
    globals: bool = True
    engine: TemplateEngine = "view"


class Config(ConfigModel):
    dev: bool = True
    app: AppConfig = ConfigField(default_factory=AppConfig)
    server: ServerConfig = ConfigField(default_factory=ServerConfig)
    log: LogConfig = ConfigField(default_factory=LogConfig)
    templates: TemplatesConfig = ConfigField(default_factory=TemplatesConfig)


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

    raise ViewInternalError("bad file type")


def load_config(
    path: Path | None = None,
    *,
    directory: Path | None = None,
) -> Config:
    """Load the configuration file.

    Args:
        path: Path to get the configuration from.
        directory: Where to look for the configuration."""
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
