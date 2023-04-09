from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import (Any, Callable, ClassVar, Generic, NewType, TypeVar, cast,
                    overload)

from typing_extensions import ParamSpec, dataclass_transform

from ._util import attempt_import, get_body

P = ParamSpec("P")
A = TypeVar("A")


class Id(Generic[A]):
    def __init__(self, value: A) -> None:
        self.value = value


_CONNECTION: Connection | None = None


class ViewModel:
    _conn: ClassVar[Connection | None]


T = TypeVar("T", bound=ViewModel)

Where = dict[str, Any]
Value = dict[str, Any]


class Model(Generic[P, T]):
    def __init__(
        self,
        ob: Callable[P, T],
        table: str,
        *,
        conn: Connection | None = None,
    ) -> None:
        self.obj = ob
        self._conn: Connection | None = conn
        self.table = table

    def __init_subclass__(cls) -> None:
        raise TypeError(
            f"Model cannot be subclassed, did you mean ViewModel?",
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

    @abstractmethod
    async def connect(self) -> None:
        ...


class MongoDriver(_Driver):
    async def create(self, where: Where, values: Value) -> None:
        ...


class Connection:
    def __init__(self, driver: _Driver):
        self.driver = driver

    def connect(self) -> None:
        ...

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
    type_check: bool = False,
    conn: Connection | None = None,
) -> Model[P, T]:
    ...


@overload
def model(
    ob_or_none: None = ...,
    *,
    type_check: bool = False,
    conn: Connection | None = None,
) -> Callable[[Callable[P, T]], Model[P, T]]:
    ...


def model(
    ob_or_none: Callable[P, T] | None | _TableNameTransport = None,
    *,
    type_check: bool = False,
    conn: Connection | None = None,
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
            raise TypeError(
                f"{ob!r} does not inherit from ViewModel, did you forget?",
            )

        body = get_body(ob)  # type: ignore
        ob = _transform(ob)  # type: ignore

        for k, v in body.items():
            ...

        return Model(ob, name, conn=conn)

    if ob_or_none:
        return impl(ob_or_none)

    return impl
