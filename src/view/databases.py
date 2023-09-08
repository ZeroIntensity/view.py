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

from ._util import attempt_import, get_body, make_hint
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
    def connect(self) -> None:
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
