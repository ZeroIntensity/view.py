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
    """Class for holding a typecode to be validated against."""

    def __init__(self, tp: type[T], codes: Iterable[TypeInfo]) -> None:
        self.tp: type[T] = tp
        self.codes: Iterable[TypeInfo] = codes
        self._compile(codes, ujson.loads)

    def check_type(self, obj: object) -> TypeGuard[T]:
        """Check if an object is the type."""
        try:
            self._cast(obj, False)
            return True
        except RuntimeError:
            return False

    def is_compatible(self, obj: object) -> bool:
        """Check if an object is compatible with the type (including with casting)."""
        try:
            self._cast(obj, True)
            return True
        except RuntimeError:
            return False

    def cast(self, obj: object) -> T:
        """Cast an object to the type.

        Raises:
            TypeValidationFailed: The object is not compatible with the type."""
        try:
            return self._cast(obj, True)
        except RuntimeError:
            raise TypeValidationError(
                f"{obj} is not assignable to {self.tp}"
            ) from None


def compile_type(tp: type[T]) -> TCValidator[T]:
    """Compile a type to a type validation object."""
    return TCValidator(tp, _build_type_codes([tp]))
