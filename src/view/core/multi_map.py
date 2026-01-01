from __future__ import annotations

from collections.abc import (
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    Sequence,
    ValuesView,
)
from typing import Any, TypeVar

from view.exceptions import ViewError

__all__ = "HasMultipleValuesError", "MultiMap"

KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")
T = TypeVar("T")


class HasMultipleValuesError(ViewError):
    """
    Multiple values were found when they were explicitly disallowed.
    """

    def __init__(self, key: Any) -> None:
        super().__init__(f"{key!r} has multiple values")


class MultiMap(Mapping[KeyT, ValueT]):
    """
    Mapping of individual keys to one or many values.
    """

    __slots__ = ("_values",)

    def __init__(self, items: Iterable[tuple[KeyT, ValueT]] = ()) -> None:
        self._values: dict[KeyT, list[ValueT]] = {}

        for key, value in items:
            values = self._values.setdefault(key, [])
            values.append(value)

    def __getitem__(self, key: KeyT, /) -> ValueT:
        """
        Get the first value if it exists, or else raise a :exc:`KeyError`.
        """

        return self._values[key][0]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[KeyT]:
        return iter(self._values)

    def __contains__(self, key: object, /) -> bool:
        return key in self._values

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, MultiMap):
            return other._values == self._values

        if isinstance(other, dict):
            return self._as_flat() == other

        return NotImplemented

    def __ne__(self, other: object, /) -> bool:
        if isinstance(other, MultiMap):
            return other._values != self._values

        return NotImplemented

    def __repr__(self) -> str:
        return f"MultiMap({self.as_sequence()})"

    def __hash__(self) -> int:
        return hash(self._values)

    def _as_flat(self) -> dict[KeyT, ValueT]:
        """
        Turn this into a "flat" representation of the mapping in which all
        keys have exactly one value.
        """
        return {key: value[0] for key, value in self._values.items()}

    def keys(self) -> KeysView[KeyT]:
        """
        Return a view of all the keys in this map.
        """
        return self._values.keys()

    def values(self) -> ValuesView[ValueT]:
        """
        Return a view of the first value for each key in the mapping.
        """
        return self._as_flat().values()

    def many_values(self) -> ValuesView[Sequence[ValueT]]:
        """
        Return a view of all values in the mapping.
        """
        return self._values.values()

    def items(self) -> ItemsView[KeyT, ValueT]:
        """
        Return a view of all items in the mapping, using the first value
        for each key.
        """
        return self._as_flat().items()

    def many_items(self) -> ItemsView[KeyT, Sequence[ValueT]]:
        """
        Return a view of all items in the mapping.
        """
        return self._values.items()

    def get_many(self, key: KeyT) -> Sequence[ValueT]:
        """
        Get one or many values for a given key.
        """
        return self._values[key]

    def get_exactly_one(self, key: KeyT) -> ValueT:
        """
        Get precisely one value for a key. If more than one value is present,
        then this raises a :exc:`HasMultipleValuesError`.
        """
        value = self._values[key]
        if len(value) != 1:
            raise HasMultipleValuesError(key)

        return value[0]

    def as_sequence(self) -> Sequence[tuple[KeyT, ValueT]]:
        """
        Return all the keys and values in a sequence of (key, value) tuples.
        """
        result: list[tuple[KeyT, ValueT]] = []
        for key, values in self._values.items():
            for value in values:
                result.append((key, value))  # noqa: PERF401

        return result

    def with_new_value(
        self, key: KeyT, value: ValueT
    ) -> MultiMap[KeyT, ValueT]:
        """
        Create a copy of this map with a new key and value included.
        """
        new_sequence = [*list(self.as_sequence()), (key, value)]
        return type(self)(new_sequence)
