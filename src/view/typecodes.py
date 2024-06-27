"""
view.py public typecode APIs.

A "typecode" is a view.py term - it's a representation of a type for fast runtime type checking.
The details of typecode internals are subject to change.

Typecodes are used internally for quickly validating received query and body route inputs.
"""
from __future__ import annotations

from typing import Generic, Iterable, TypeVar

import ujson
from typing_extensions import TypeGuard

from _view import TCPublic

from ._loader import _build_type_codes
from .exceptions import TypeValidationError
from .typing import TypeInfo

__all__ = "TCValidator", "compile_type"
T = TypeVar("T")


class TCValidator(TCPublic, Generic[T]):
    """
    Class for holding a typecode to be validated against.

    A "typecode" is a view.py term - it's a representation of a type for fast runtime type checking.
    The details of typecode internals are subject to change.

    It's highly unlikely that you would need to instantiate this class yourself - it should only be referenced directly for type hinting purposes.

    The constructor of this class is considered unstable - do not expect backwards compatibility!
    Use the `compile_type` function instead.
    """

    def __init__(self, tp: type[T], codes: Iterable[TypeInfo]) -> None:
        self.tp: type[T] = tp
        """Original, unmodified type passed to `compile_type()`."""
        self.codes: Iterable[TypeInfo] = codes
        """Iterable containing `TypeInfo` objects. Note that `TypeInfo` objects themself are considered unstable."""
        self._compile(codes, ujson.loads)

    def check_type(self, obj: object) -> TypeGuard[T]:
        """
        Check if an object *is* the type. This will not cast parameters, so it acts as a `TypeGuard`.

        Args:
            obj: Object to check against.

        Example:
            ```py
            from view import compile_type

            tc = compile_type(int)
            val = 1

            if tc.check_type(val):
                assert type(val) == int
            else:
                assert type(val) != int
            ```
        """
        try:
            self._cast(obj, False)
            return True
        except (ValueError, TypeError):
            return False

    def is_compatible(self, obj: object) -> bool:
        """
        Check if an object is compatible with the type (including with casting).

        Args:
            obj: Object to check against.

        Example:
            ```py
            from view import compile_type

            tc = compile_type(int)

            assert tc.is_compatible('1') is True  # '1' can be casted to an integer
            assert tc.is_compatible('hello') is False  # 'hello' cannot be casted to an integer
            ```
        """
        try:
            self._cast(obj, True)
            return True
        except (ValueError, TypeError):
            return False

    def cast(self, obj: object) -> T:
        """
        Attempt to turn `obj` into the underlying type.

        Args:
            obj: Object to cast from.

        Raises:
            TypeValidationError: The object is not compatible with the type.

        Example:
            ```py
            from view import compile_type

            tc = compile_type(int)
            obj = tc.cast("1")
            assert obj == 1
            ```
        """
        try:
            return self._cast(obj, True)
        except (ValueError, TypeError):
            raise TypeValidationError(f"{obj} is not assignable to {self.tp}") from None


def compile_type(tp: type[T]) -> TCValidator[T]:
    """
    Compile a type to a type validation object.

    Args:
        tp: Type to compile. Note that this can't be just *any* type, it has to be something that view.py supports (such as `str`, `int`, or something that implements `__view_body__`).

    Example:
        ```py
        from view import compile_type

        validator = compile_type(str | int)
        assert validator.is_compatible('1')  # True
        ```
    """
    return TCValidator(tp, _build_type_codes([tp]))
