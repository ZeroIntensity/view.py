"""
view.py configuration APIs

This module contains `load_config`, `Config`, and all subcategories of `Config`.
"""

from __future__ import annotations
import runpy
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any, Dict, List, Literal, Union
from pydantic import Field
from pydantic_settings import BaseSettings
from typing_extensions import TypeAlias
import toml
from .exceptions import ViewInternalError
from .typing import TemplateEngine

__all__ = (
    "AppConfig",
    "ServerConfig",
    "LogConfig",
    "MongoConfig",
    "PostgresConfig",
    "SQLiteConfig",
    "DatabaseConfig",
    "TemplatesConfig",
    "BuildStep",
    "BuildConfig",
    "Config",
    "make_preset",
    "load_config",
)


class AppConfig(BaseSettings):
    loader: Literal["manual", "simple", "filesystem", "patterns", "custom"] = "manual"
    app_path: str = "app.py:app"
    uvloop: Union[Literal["decide"], bool] = "decide"
    loader_path: Path = Path("./routes")

class ServerConfig(BaseSettings):
    host: IPv4Address = IPv4Address("0.0.0.0")
    port: int = 5000
    backend: Literal["uvicorn", "hypercorn", "daphne"] = "uvicorn"
    extra_args: Dict[str, Any] = Field(default_factory=dict)


class LogConfig(BaseSettings):
    level: Union[Literal["debug", "info", "warning", "error", "critical"], int] = "info"
    fancy: bool = True
    server_logger: bool = False
    pretty_tracebacks: bool = True
    startup_message: bool = True


class MongoConfig(BaseSettings):
    host: IPv4Address
    port: int
    username: str
    password: str
    database: str


class PostgresConfig(BaseSettings):
    database: str
    user: str
    password: str
    host: IPv4Address
    port: int


class SQLiteConfig(BaseSettings):
    file: Path


class MySQLConfig(BaseSettings):
    host: IPv4Address
    user: str
    password: str
    database: str


class DatabaseConfig(BaseSettings):
    type: Literal["sqlite", "mysql", "postgres", "mongo"] = "sqlite"
    mongo: Union[MongoConfig, None] = None
    postgres: Union[PostgresConfig, None] = None
    sqlite: Union[SQLiteConfig, None] = SQLiteConfig(file=Path("view.db"))
    mysql: Union[MySQLConfig, None] = None


class TemplatesConfig(BaseSettings):
    directory: Path = Path("./templates")
    locals: bool = True
    globals: bool = True
    engine: TemplateEngine = "view"


Platform: TypeAlias = Literal[
    "windows", "mac", "linux", "macOS", "Windows", "Linux", "Mac", "MacOS"
]


class BuildStep(BaseSettings):
    platform: Union[List[Platform], Platform, None] = None
    requires: List[str] = Field(default_factory=list)
    command: Union[str, None, List[str]] = None
    script: Union[Path, None, List[Path]] = None


class BuildConfig(BaseSettings):
    path: Path = Path("./build")
    default_steps: Union[List[str], None] = None
    steps: Dict[str, Union[BuildStep, List[BuildStep]]] = Field(
        default_factory=dict
    )
    parallel: bool = False


class Config(BaseSettings):
    dev: bool = True
    env: Dict[str, Any] = Field(default_factory=dict)
    app: AppConfig = Field(default_factory=AppConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    templates: TemplatesConfig = Field(default_factory=TemplatesConfig)
    build: BuildConfig = Field(default_factory=BuildConfig)


B_OPEN = "{"
B_CLOSE = "}"
B_OC = "{}"


def make_preset(tp: str, loader: str) -> str:
    if tp == "toml":
        return f"""# See https://view.zintensity.dev/getting-started/configuration/
dev = true # Development mode

[app]
loader = "{loader}" # Loader strategy
app_path = "app.py:app" # Location and name of the app instance
uvloop = "decide" # Use uvloop for the event loop
loader_path = "routes/" # Loader-specific path

[server]
host = "0.0.0.0" # Address to bind
port = 5000 # Port to bind
backend = "uvicorn" # ASGI server

[server.extra_args]
# ASGI backend specific arguments
# workers = 4

[log]
level = "info" # Log level
server_logger = false # Show ASGI servers raw logs
fancy = true # Enable fancy output
pretty_tracebacks = true # Use Rich exceptions
startup_message = true # Show view.py welcome message

[templates]
directory = "./templates" # Template search directory
locals = true # Allow templates to access local variables when rendered
globals = true # Same as above, but with global variables
engine = "view" # Default template engine
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

    if tp == "py":
        return """from view import Config

CONFIG = Config()"""

    raise ViewInternalError("bad file type")


def load_config(
    path: Path | None = None,
    *,
    directory: Path | None = None,
) -> Config:
    """
    Load the configuration file. If there is no existing configuration file, a virtual configuration is generated with default values.

    Args:
        path: Path to get the configuration from.
        directory: Where to look for the configuration.
    """
    paths = (
        "view.toml",
        "view.json",
        "view_config.py",
        "config.py",
    )

    if path:
        if directory:
            return Config.model_validate(toml.load(directory / path))
            # Not sure why someone would do this, but it's good to support it
        return Config.model_validate(toml.load(path))

    for i in paths:
        p = Path(i) if not directory else directory / i

        if not p.exists():
            continue

        if p.suffix == ".py":
            glbls = runpy.run_path(str(p))
            config = glbls.get("CONFIG")
            if not isinstance(config, Config):
                raise TypeError(f"{config!r} is not an instance of Config")
            return config

        return Config.model_validate(toml.load(p))

    return Config()
