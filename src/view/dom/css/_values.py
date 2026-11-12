from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import (
    ClassVar,
    Generic,
    Literal,
    TypeAlias,
    TypeVar,
    Union,
    get_args,
)

GlobalKeyword: TypeAlias = Literal[
    "inherit", "initial", "revert", "revert-layer", "unset"
]
LengthUnit: TypeAlias = Literal[
    "px",
    "cm",
    "mm",
    "Q",
    "in",
    "pc",
    "pt",
    "em",
    "ex",
    "cap",
    "ch",
    "ic",
    "lh",
    "rem",
    "rex",
    "rcap",
    "rch",
    "ric",
    "rlh",
    "vw",
    "vh",
    "vi",
    "vb",
    "vmin",
    "vmax",
    "svw",
    "svh",
    "svi",
    "svb",
    "svmin",
    "svmax",
    "lvw",
    "lvh",
    "lvi",
    "lvb",
    "lvmin",
    "lvmax",
    "dvw",
    "dvh",
    "dvi",
    "dvb",
    "dvmin",
    "dvmax",
    "cqw",
    "cqh",
    "cqi",
    "cqb",
    "cqmin",
    "cqmax",
]


def _number(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("CSS numbers must be integers or floats")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("CSS numbers must be finite")
        if value.is_integer():
            return str(int(value))
    return str(value)


@dataclass(frozen=True, slots=True)
class _Dimension:
    value: float
    unit: str
    _units: ClassVar[frozenset[str]] = frozenset()

    def __post_init__(self) -> None:
        _number(self.value)
        if self.unit not in self._units:
            raise ValueError(
                f"Invalid {type(self).__name__} unit: {self.unit!r}"
            )

    def as_css(self) -> str:
        return f"{_number(self.value)}{self.unit}"

    def __str__(self) -> str:
        return self.as_css()


@dataclass(frozen=True, slots=True)
class Length(_Dimension):
    unit: LengthUnit
    _units: ClassVar[frozenset[str]] = frozenset(get_args(LengthUnit))


class Pixels(Length):
    __slots__ = ()

    def __init__(self, value: float) -> None:
        super().__init__(value, "px")


class Ems(Length):
    __slots__ = ()

    def __init__(self, value: float) -> None:
        super().__init__(value, "em")


class Rems(Length):
    __slots__ = ()

    def __init__(self, value: float) -> None:
        super().__init__(value, "rem")


class ViewportWidth(Length):
    __slots__ = ()

    def __init__(self, value: float) -> None:
        super().__init__(value, "vw")


class ViewportHeight(Length):
    __slots__ = ()

    def __init__(self, value: float) -> None:
        super().__init__(value, "vh")


class Percentage(_Dimension):
    __slots__ = ()
    _units: ClassVar[frozenset[str]] = frozenset(("%",))

    def __init__(self, value: float) -> None:
        super().__init__(value, "%")


@dataclass(frozen=True, slots=True)
class Angle(_Dimension):
    unit: Literal["deg", "grad", "rad", "turn"] = "deg"
    _units: ClassVar[frozenset[str]] = frozenset(
        ("deg", "grad", "rad", "turn")
    )


@dataclass(frozen=True, slots=True)
class Time(_Dimension):
    unit: Literal["s", "ms"] = "s"
    _units: ClassVar[frozenset[str]] = frozenset(("s", "ms"))


@dataclass(frozen=True, slots=True)
class Frequency(_Dimension):
    unit: Literal["Hz", "kHz"] = "Hz"
    _units: ClassVar[frozenset[str]] = frozenset(("Hz", "kHz"))


@dataclass(frozen=True, slots=True)
class Resolution(_Dimension):
    unit: Literal["dpi", "dpcm", "dppx", "x"] = "dppx"
    _units: ClassVar[frozenset[str]] = frozenset(("dpi", "dpcm", "dppx", "x"))


class Fractions(_Dimension):
    __slots__ = ()
    _units: ClassVar[frozenset[str]] = frozenset(("fr",))

    def __init__(self, value: float) -> None:
        super().__init__(value, "fr")


def _validate_raw(value: object) -> None:
    if not isinstance(value, str):
        raise TypeError("Raw CSS must be a string")


@dataclass(frozen=True, slots=True)
class RawCSS:
    value: str

    def __post_init__(self) -> None:
        _validate_raw(self.value)

    def as_css(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.as_css()


T_co = TypeVar("T_co", covariant=True)


@dataclass(frozen=True, slots=True)
class Important(Generic[T_co]):
    value: T_co


PropertyValue: TypeAlias = Union[
    T_co, GlobalKeyword, RawCSS, Important[Union[T_co, GlobalKeyword, RawCSS]]
]
CSSValue: TypeAlias = Union[
    str,
    int,
    float,
    _Dimension,
    RawCSS,
    Important["CSSValue"],
    Sequence["CSSValue"],
]


def render_value(value: CSSValue, *, nested: bool = False) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (_Dimension, RawCSS)):
        return value.as_css()
    if isinstance(value, Important):
        if nested:
            raise ValueError("!important must apply to the entire declaration")
        return f"{render_value(value.value, nested=True)} !important"
    if isinstance(value, Sequence):
        if not value:
            raise ValueError("CSS value sequences cannot be empty")
        separator = " " if isinstance(value, tuple) else ", "
        return separator.join(
            render_value(item, nested=True) for item in value
        )
    return _number(value)
