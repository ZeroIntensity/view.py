from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Set, TypeVar, Union, get_origin, get_type_hints

from typing_extensions import Annotated, Self, dataclass_transform, get_args

from ._util import is_annotated, is_union, needs_dep
from .exceptions import InvalidDatabaseSchemaError
from .routing import BodyParam
from .typing import ViewBody

try:
    import aiosqlite
except ModuleNotFoundError as e:
    needs_dep("aiosqlite", e, "databases")

try:
    import mysql.connector
except ModuleNotFoundError as e:
    needs_dep("mysql-connector-python", e, "databases")

try:
    import psycopg2
except ModuleNotFoundError as e:
    needs_dep("psycopg2-binary", e, "databases")

try:
    import pymongo
except ModuleNotFoundError as e:
    needs_dep("pymongo", e, "databases")

__all__ = ("Model",)
NoneType = type(None)


class _Connection(ABC):
    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    @abstractmethod
    async def insert(self, table: str, json: dict) -> None:
        ...

    @abstractmethod
    async def find(self, table: str, json: dict) -> None:
        ...

    @abstractmethod
    async def migrate(self, table: str, vbody: dict) -> None:
        ...


_SQL_TYPES: dict[type, str] = {
    str: "TEXT",
    float: "FLOAT",
    int: "INT",
    bytes: "BLOB",
    datetime: "DATETIME",
}


def _sql_translate(vbody: dict) -> str:
    items: list[str] = []

    for k, v in vbody.items():
        tp = _SQL_TYPES.get(v)

        if tp:
            items.append(f"{k} {tp} NOT NULL")
            continue

        flags = ["NOT NULL"]
        origin = get_origin(v)

        if is_union(type(v)):
            args = get_args(v)
            if (len(args) != 2) or (NoneType not in args):
                raise InvalidDatabaseSchemaError(
                    "union types are not allowed in databases, other than None",
                )

            flags.pop(0)
            v = args[0] if args[0] is not None else args[1]

        if is_annotated(v):
            print(get_args(v))

        tp = _SQL_TYPES.get(v)

        if tp:
            items.append(f"{k} {tp}{' '.join(flags)}")
            continue

        raise InvalidDatabaseSchemaError(f"{v} is not a supported type")

    return ", ".join(items)


class _PostgresConnection(_Connection):
    def __init__(
        self,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def create_database_connection(self):
        return psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    async def connect(self) -> None:
        try:
            self.connection = await asyncio.to_thread(self.create_database_connection)
            self.cursor = await asyncio.to_thread(self.connection.cursor)  # type: ignore
        except psycopg2.Error as e:
            raise ValueError(
                "Unable to connect to the database - invalid credentials"
            ) from e

    async def close(self) -> None:
        if self.connection is not None:
            await asyncio.to_thread(self.connection.close)
            self.connection = None
            self.cursor = None


class _SQLiteConnection(_Connection):
    def __init__(self, database_file: str) -> None:
        self.database_file = database_file
        self.connection: aiosqlite.Connection | None = None
        self.cursor: aiosqlite.Cursor | None = None

    async def connect(self) -> None:
        self.connection = await aiosqlite.connect(self.database_file)
        self.cursor = await self.connection.cursor()

    async def close(self) -> None:
        if self.connection is not None:
            assert self.cursor is not None
            await self.cursor.close()
            await self.connection.close()
            self.connection = None
            self.cursor = None

    async def insert(self, table: str, json: dict) -> None:
        ...

    async def find(self, table: str, json: dict) -> None:
        ...

    async def migrate(self, table: str, vbody: dict):
        assert self.cursor is not None
        sql = _sql_translate(vbody)
        print(sql)
        await self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({sql})")


class _MySQLConnection:
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
    ) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    async def connect(self) -> None:
        try:
            self.connection = await asyncio.to_thread(
                mysql.connector.connect,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )

            self.cursor = await asyncio.to_thread(self.connection.cursor)
        except mysql.connector.Error as e:
            raise ValueError(
                "Unable to connect to the database - invalid credentials"
            ) from e

    async def close(self):
        if self.connection is not None:
            assert self.cursor is not None
            await asyncio.to_thread(self.cursor.close)
            await asyncio.to_thread(self.connection.close)
            self.connection = None
            self.cursor = None


class _MongoDBConnection:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.client = None
        self.db = None

    async def connect(self):
        self.client = await asyncio.to_thread(
            pymongo.MongoClient,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            authSource=self.database,
        )
        self.db = self.client[self.database]

    async def close(self):
        if self.client is not None:
            await asyncio.to_thread(self.client.close)
            self.client = None
            self.db = None


class _Meta(Enum):
    HASH = 0
    ID = 1
    EXCLUDE = 2


class _ModelMeta:
    def __init__(self, tp: _Meta):
        self.tp = tp


T = TypeVar("T")
Hashed = Annotated[T, _ModelMeta(_Meta.HASH)]
Id = Annotated[T, _ModelMeta(_Meta.ID)]
Exclude = Annotated[T, _ModelMeta(_Meta.EXCLUDE)]


@dataclass_transform()
class Model:
    view_initialized: ClassVar[bool] = False
    conn: ClassVar[Union[_Connection, None]] = None
    exclude: ClassVar[Set[str]]
    __view_body__: ClassVar[ViewBody] = {}
    __view_table__: ClassVar[str]

    def __init__(self, *args: Any, **kwargs: Any):
        for index, k in enumerate(self.__view_body__):
            if index >= len(args):
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, args[index])

    def __init_subclass__(cls, **kwargs: Any):
        cls.__view_table__ = kwargs.get("table") or ("vpy_" + cls.__name__.lower())
        model_hints = get_type_hints(Model)
        actual_hints = get_type_hints(cls)
        params = {
            k: actual_hints[k] for k in (model_hints.keys() ^ actual_hints.keys())
        }

        for k, v in params.items():
            df = cls.__dict__.get(k)
            if df:
                cls.__view_body__[k] = BodyParam(types=v, default=df)
            else:
                cls.__view_body__[k] = v

    def __repr__(self) -> str:
        body = [f"{k}={repr(getattr(self, k))}" for k in self.__view_body__]
        return f"{type(self).__name__}({', '.join(body)})"

    __str__ = __repr__

    @classmethod
    def find(cls) -> list[Self]:
        ...

    @classmethod
    def unique(cls) -> Self:
        ...

    def exists(self) -> bool:
        ...

    def save(self) -> None:
        conn = self._assert_conn()

        conn.insert(self.__view_table__, self._json())

    def _json(self) -> dict[str, Any]:
        ...

    def json(self) -> dict[str, Any]:
        ...

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        ...

    @classmethod
    def _assert_conn(cls) -> _Connection:
        if not cls.conn:
            raise Exception

        return cls.conn
