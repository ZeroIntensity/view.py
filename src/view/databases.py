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


class Model(Generic[P, T]):
    def __init__(self, ob: Callable[P, T]):
        self.obj = ob
        self._conn: Connection | None = None

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
    async def create(self, where: Where, values: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def update(self, where: Where, values: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def delete(self, where: Where) -> None:
        ...

    @abstractmethod
    async def connect(self) -> None:
        ...


class Connection:
    def __init__(self, driver: _Driver):
        ...

    def connect(self) -> None:
        ...

    def close(self) -> None:
        ...


def _init(self: Any, *args: Any, **kwargs: Any):
    ...


@dataclass_transform()
def _transform(cls: type[A]) -> type[A]:
    cls.__init__ = _init
    return cls


@overload
def model(
    ob_or_none: Callable[P, T],
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
    ob_or_none: Callable[P, T] | None = None,
    *,
    type_check: bool = False,
    conn: Connection | None = None,
) -> Model[P, T] | Callable[[Callable[P, T]], Model[P, T]]:
    def impl(ob: Callable[P, T]) -> Model[P, T]:
        if not issubclass(cast(type, ob), ViewModel):
            raise TypeError(
                f"{ob!r} does not inherit from ViewModel, did you forget?",
            )

        body = get_body(ob)
        ob = _transform(ob)  # type: ignore

        for k, v in body.items():
            ...

        return Model(ob)

    if ob_or_none:
        return impl(ob_or_none)

    return impl
