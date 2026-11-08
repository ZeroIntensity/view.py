from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeAlias, cast

from typing_extensions import Unpack

from ._properties import CSSProperties
from ._values import (
    Angle,
    CSSValue,
    Ems,
    Fractions,
    Frequency,
    GlobalKeyword,
    Important,
    Length,
    LengthUnit,
    Percentage,
    Pixels,
    RawCSS,
    Rems,
    Resolution,
    Time,
    ViewportHeight,
    ViewportWidth,
    render_value,
)

__all__ = (
    "Angle",
    "AtRule",
    "CSSProperties",
    "CSSRule",
    "CSSValue",
    "Ems",
    "Fractions",
    "Frequency",
    "GlobalKeyword",
    "Important",
    "Length",
    "LengthUnit",
    "Percentage",
    "Pixels",
    "RawCSS",
    "Rems",
    "Resolution",
    "Rule",
    "Stylesheet",
    "Time",
    "ViewportHeight",
    "ViewportWidth",
    "at_rule",
    "raw",
    "rule",
    "stylesheet",
)


def _header(value: object) -> None:
    if not isinstance(value, str):
        raise TypeError("CSS selectors and at-rule headers must be strings")
    if not value.strip():
        raise ValueError("CSS selectors and at-rule headers cannot be empty")


def _property_name(name: object) -> str:
    if not isinstance(name, str):
        raise TypeError("CSS property names must be strings")
    if name.startswith("--"):
        if len(name) == 2:
            raise ValueError("Custom properties must have a name after '--'")
        return name
    if not name or not all(c.isalnum() or c in "_-" for c in name):
        raise ValueError(f"Invalid CSS property name: {name!r}")
    return name.removesuffix("_").replace("_", "-")


@dataclass(frozen=True, slots=True)
class Rule:
    selector: str
    properties: Mapping[str, CSSValue]

    def __post_init__(self) -> None:
        _header(self.selector)
        # Render once so mutable input collections cannot change a stylesheet.
        rendered = {
            _property_name(name): render_value(value)
            for name, value in self.properties.items()
        }
        object.__setattr__(self, "properties", MappingProxyType(rendered))

    def as_css_stream(self) -> Iterator[str]:
        yield f"{self.selector} {{"
        for name, value in self.properties.items():
            yield f"    {name}: {value};"
        yield "}"

    def as_css(self) -> str:
        return "\n".join(self.as_css_stream()) + "\n"

    def __str__(self) -> str:
        return self.as_css()


def rule(
    selector: str,
    /,
    *,
    declarations: Mapping[str, CSSValue] | None = None,
    **properties: Unpack[CSSProperties],
) -> Rule:
    unknown = properties.keys() - CSSProperties.__annotations__.keys()
    if unknown:
        names = ", ".join(sorted(unknown))
        raise TypeError(f"Unknown CSS properties: {names}")
    values = dict(declarations) if declarations is not None else {}
    values.update(cast("dict[str, CSSValue]", properties))
    return Rule(selector, values)


@dataclass(frozen=True, slots=True, init=False)
class AtRule:
    header: str
    rules: tuple[CSSRule, ...]

    def __init__(self, header: str, rules: Iterable[CSSRule] = ()) -> None:
        _header(header)
        if not header.startswith("@"):
            raise ValueError("An at-rule header must start with '@'")
        object.__setattr__(self, "header", header)
        object.__setattr__(self, "rules", _collect_rules(rules))

    def as_css_stream(self) -> Iterator[str]:
        yield f"{self.header} {{"
        for child in self.rules:
            for line in _rule_stream(child):
                yield f"    {line}"
        yield "}"

    def as_css(self) -> str:
        return "\n".join(self.as_css_stream()) + "\n"

    def __str__(self) -> str:
        return self.as_css()


CSSRule: TypeAlias = Rule | AtRule | RawCSS


def _collect_rules(rules: Iterable[object]) -> tuple[CSSRule, ...]:
    result: list[CSSRule] = []
    for item in rules:
        if not isinstance(item, (Rule, AtRule, RawCSS)):
            raise TypeError(
                "Stylesheets must contain Rule, AtRule or RawCSS objects"
            )
        result.append(item)
    return tuple(result)


def _rule_stream(item: CSSRule) -> Iterator[str]:
    if isinstance(item, RawCSS):
        yield from item.as_css().splitlines()
    else:
        yield from item.as_css_stream()


def at_rule(header: str, /, *rules: CSSRule) -> AtRule:
    return AtRule(header, rules)


def raw(value: str, /) -> RawCSS:
    return RawCSS(value)


@dataclass(frozen=True, slots=True, init=False)
class Stylesheet:
    rules: tuple[CSSRule, ...]

    def __init__(self, rules: Iterable[CSSRule] = ()) -> None:
        object.__setattr__(self, "rules", _collect_rules(rules))

    def as_css_stream(self) -> Iterator[str]:
        for item in self.rules:
            yield from _rule_stream(item)

    def as_css(self) -> str:
        return "".join(line + "\n" for line in self.as_css_stream())

    def __str__(self) -> str:
        return self.as_css()


def stylesheet(function: Callable[[], Iterable[CSSRule]]) -> Stylesheet:
    return Stylesheet(function())
