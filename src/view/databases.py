from __future__ import annotations

import asyncio
import sqlite3
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar, TypeVar, Union, get_type_hints

import mysql.connector
import psycopg2
import pymongo
from typing_extensions import Annotated, Self, dataclass_transform

from .routing import BodyParam
from .typing import ViewBody

__all__ = ("Model",)


class _Connection(ABC):
    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...


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
            self.connection = await asyncio.to_thread(
                self.create_database_connection
            )
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


class _SQLiteConnection:
    def __init__(self, database_file: str) -> None:
        self.database_file = database_file
        self.connection: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    async def connect(self) -> None:
        self.connection = await asyncio.to_thread(
            sqlite3.connect, self.database_file
        )
        self.cursor = await asyncio.to_thread(self.connection.cursor)  # type: ignore

    async def close(self) -> None:
        if self.connection is not None:
            assert self.cursor is not None
            await asyncio.to_thread(self.cursor.close)
            await asyncio.to_thread(self.connection.close)
            self.connection = None
            self.cursor = None


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


class _ModelMeta:
    def __init__(self, tp: _Meta):
        self.tp = tp


T = TypeVar("T")
Hashed = Annotated[T, _ModelMeta(_Meta.HASH)]
Id = Annotated[T, _ModelMeta(_Meta.ID)]


@dataclass_transform()
class Model:
    view_initialized: ClassVar[bool] = False
    __view_body__: ClassVar[ViewBody] = {}
    view_conn: Union[_Connection, None] = None

    def __init__(self, *args: Any, **kwargs: Any):
        ...

    def __init_subclass__(cls):
        model_hints = get_type_hints(Model)
        actual_hints = get_type_hints(cls)
        params = {
            k: actual_hints[k]
            for k in (model_hints.keys() ^ actual_hints.keys())
        }

        for k, v in params.items():
            df = cls.__dict__.get(k)
            if df:
                cls.__view_body__[k] = BodyParam(types=v, default=df)
            else:
                cls.__view_body__[k] = v

    @classmethod
    def find(cls) -> list[Self]:
        ...

    @classmethod
    def unique(cls) -> Self:
        ...

    def exists(self) -> bool:
        ...

    def save(self) -> None:
        ...

    def json(self) -> dict[str, Any]:
        ...

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        ...
