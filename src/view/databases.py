from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    TypeVar,
    cast,
    overload,
    Dict,
)

from typing_extensions import ParamSpec, dataclass_transform

from ._util import attempt_import, make_hint
from .exceptions import MistakeError

P = ParamSpec("P")
A = TypeVar("A")


class ViewModel:
    _conn: ClassVar[_Connection | None]


T = TypeVar("T", bound=ViewModel)

Where = Dict[str, Any]
Value = Dict[str, Any]


class Model(Generic[P, T]):
    def __init__(
        self,
        ob: Callable[P, T],
        table: str,
        *,
        conn: _Connection | None = None,
    ) -> None:
        self.obj = ob
        self._conn: _Connection | None = conn
        self.table = table

    def __init_subclass__(cls) -> None:
        raise MistakeError(
            "Model cannot be subclassed, did you mean ViewModel?",
            hint=make_hint("This should be ViewModel, not Model"),
        )

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.obj(*args, **kwargs)  # type: ignore

    async def find(
        self,
        limit: int = -1,
        offset: int | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> list[T]:
        ...


class _Driver(ABC):
    @classmethod
    @abstractmethod
    def ensure(cls) -> None:
        ...

    @abstractmethod
    async def find(
        self, where: Where, limit: int = -1, offset: int = 0
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def create(self, where: Where, values: Value) -> None:
        ...

    @abstractmethod
    async def update(self, where: Where, values: Value) -> None:
        ...

    @abstractmethod
    async def delete(self, where: Where) -> None:
        ...


class MongoDriver(_Driver):
    pymongo: ClassVar[Any]

    @classmethod
    def ensure(cls):
        cls.pymongo = attempt_import("pymongo")

    async def create(self, where: Where, values: Value) -> None:
        ...


class _Connection(ABC):
    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...


def _init(self: Any, *args: Any, **kwargs: Any):
    ...


class _TableNameTransport(Generic[P, T]):
    def __init__(self, name: str, ob: Model[P, T] | Callable[P, T]):
        self.name = name
        self.ob = ob


def table(
    name: str,
):
    @overload
    def wrapper(ob: Model[P, T]) -> Model[P, T]:
        ...

    @overload
    def wrapper(ob: Callable[P, T]) -> _TableNameTransport[P, T]:
        ...

    def wrapper(
        ob: Model[P, T] | Callable[P, T]
    ) -> Model[P, T] | _TableNameTransport[P, T]:
        if isinstance(ob, Model):
            ob.table = name
            return ob
        return _TableNameTransport(name, ob)

    return wrapper


@dataclass_transform()
def _transform(cls: type[A]) -> type[A]:
    cls.__init__ = _init
    return cls


@overload
def model(
    ob_or_none: Callable[P, T] | _TableNameTransport,
    *,
    conn: _Connection | None = None,
    table_name: str = "view",
) -> Model[P, T]:
    ...


@overload
def model(
    ob_or_none: None = ...,
    *,
    conn: _Connection | None = None,
    table_name: str = "view",
) -> Callable[[Callable[P, T]], Model[P, T]]:
    ...


def model(
    ob_or_none: Callable[P, T] | None | _TableNameTransport = None,
    *,
    conn: _Connection | None = None,
    table_name: str = "view",
) -> Model[P, T] | Callable[[Callable[P, T]], Model[P, T]]:
    def impl(raw_ob: Callable[P, T] | _TableNameTransport) -> Model[P, T]:
        if isinstance(raw_ob, _TableNameTransport):
            name = raw_ob.name
            ob = raw_ob.ob
        else:
            name = table_name
            ob = raw_ob

        if not issubclass(cast(type, ob), ViewModel):
            if isinstance(ob, type):
                msg = f"{ob.__name__} does not inherit from ViewModel, did you forget?"  # noqa

            msg = f"{ob!r} does not inherit from ViewModel, did you forget?"

            raise MistakeError(
                msg, hint=make_hint("This should inherit from ViewModel")
            )

        body = get_body(ob)  # type: ignore
        ob = _transform(ob)  # type: ignore

        for k, v in body.items():
            ...

        return Model(ob, name, conn=conn)

    if ob_or_none: 
        return impl(ob_or_none)

    return impl



#database
import psycopg2  # Import the PostgreSQL driver library
import sqlite3  # Import the SQLite3 driver library
import mysql.connector # Import the MySQL driver library
import pymongo # Import the MongoDB driver library
import asyncio


class PostgresConnection(_Connection):
    '''
    This class is used to connect to a PostgreSQL database. Pass the connection details as parameters to the constructor. \n
        ``` 
        obj = PostgresConnection(
            "database": **db_name**,
            "user": **user_name**,
            "password": **password**,
            "host": **host_name**,
            "port": **port_num**
        )
        
        ```
    '''

    def __init__(
        self, 
        database: str  | None = None,
        user: str  | None = None,
        password: str  | None = None,
        host: str  | None = None,
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
        # ASGI error comes if I put this in connect method
        return psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    async def connect(self):
        '''
            This method is used to connect to the database. \n
        '''
        try:
            self.connection = await asyncio.to_thread(self.create_database_connection)
            self.cursor = await asyncio.to_thread(self.connection.cursor)
        except psycopg2.Error as e:
            raise ValueError("Unable to connect to the database - invalid credentials") from e
        
    
    async def close(self):
        '''
            This method is used to close the connection to the database. \n
        '''
        if self.connection is not None:
            await asyncio.to_thread(self.connection.close)
            self.connection = None
            self.cursor = None




class SQLiteConnection:
    '''
    This class is used to connect to an SQLite database. Pass the database file path as a parameter to the constructor.
    Example usage:
    
    obj = SQLiteConnection("mydb.sqlite")
    '''
    
    def __init__(self, database_file: str):
        self.database_file = database_file
        self.connection = None
        self.cursor = None

    async def connect(self):
        '''
        This method is used to connect to the SQLite database.
        '''
        try:
            self.connection = await asyncio.to_thread(sqlite3.connect, self.database_file)
            self.cursor = await asyncio.to_thread(self.connection.cursor)
        except sqlite3.Error as e:
            raise ValueError("Unable to connect to the database - invalid file or permissions") from e

    # async def execute_query(self, query: str, params: tuple = None):
    #     '''
    #     This method is used to execute a query on the database.
    #     '''
    #     if self.cursor is not None:
    #         try:
    #             if params:
    #                 await asyncio.to_thread(self.cursor.execute, query, params)
    #             else:
    #                 await asyncio.to_thread(self.cursor.execute, query)
    #             return self.cursor.fetchall()
    #         except sqlite3.Error as e:
    #             raise ValueError("Error executing query") from e
    #     else:
    #         raise ValueError("Database connection is not established")

    async def close(self):
        '''
        This method is used to close the connection to the database.
        '''
        if self.connection is not None:
            await asyncio.to_thread(self.cursor.close)
            await asyncio.to_thread(self.connection.close)
            self.connection = None
            self.cursor = None



class MySQLConnection:
    '''
    This class is used to connect to a MySQL database. Pass the connection details as parameters to the constructor.
    Example usage:
    
    obj = MySQLConnection(
        host="localhost",
        user="username",
        password="password",
        database="mydb"
    )
    '''
    
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    async def connect(self):
        '''
        This method is used to connect to the MySQL database.
        '''
        try:
            self.connection = await asyncio.to_thread(
                mysql.connector.connect,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = await asyncio.to_thread(self.connection.cursor)
        except mysql.connector.Error as e:
            raise ValueError("Unable to connect to the database - invalid credentials") from e

    # async def execute_query(self, query: str, params: tuple = None):
    #     '''
    #     This method is used to execute a query on the database.
    #     '''
    #     if self.cursor is not None:
    #         try:
    #             if params:
    #                 await asyncio.to_thread(self.cursor.execute, query, params)
    #             else:
    #                 await asyncio.to_thread(self.cursor.execute, query)
    #             return self.cursor.fetchall()
    #         except mysql.connector.Error as e:
    #             raise ValueError("Error executing query") from e
    #     else:
    #         raise ValueError("Database connection is not established")

    async def close(self):
        '''
        This method is used to close the connection to the database.
        '''
        if self.connection is not None:
            await asyncio.to_thread(self.cursor.close)
            await asyncio.to_thread(self.connection.close)
            self.connection = None
            self.cursor = None



class MongoDBConnection:
    '''
    This class is used to connect to a MongoDB database. Pass the connection details as parameters to the constructor.
    Example usage:
    ```
    obj = MongoDBConnection(
        host="localhost",
        port=27017,
        username="username",
        password="password",
        database="mydb"
    )
    ```
    '''

    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.client = None
        self.db = None

    async def connect(self):
        '''
        This method is used to connect to the MongoDB database.
        '''
        try:
            self.client = await asyncio.to_thread(
                pymongo.MongoClient,
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                authSource=self.database
            )
            self.db = self.client[self.database]
            print("connection mongo done")
        except pymongo.errors.ConnectionFailure as e:
            raise ValueError("Unable to connect to the database - connection failure") from e

    async def close(self):
        '''
        This method is used to close the connection to the MongoDB database.
        '''
        if self.client is not None:
            await asyncio.to_thread(self.client.close)
            self.client = None
            self.db = None