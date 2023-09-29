from __future__ import annotations

from typing import Any, Literal

from .app import InputDoc
from .typing import DocsType

_PRIMITIVES = {
    str: "string",
    int: "integer",
    dict: "object",
    Any: "any",
    bool: "boolean",
    float: "double",
    None: "null",
}


def _tp_name(tp: Any) -> str:
    prim = _PRIMITIVES.get(tp)
    if prim:
        return f"`{prim}`"

    return f"`{tp.__name__}`"


def _format_type(tp: tuple[type[Any], ...], types: list[Any]) -> str:
    if len(tp) == 1:
        return _tp_name(tp[0])

    final = ""

    for index, i in enumerate(tp):
        if (index + 1) == len(tp):
            final += _tp_name(i)
        else:
            final += f"{_tp_name(i)} | "

    return final


def _make_table(
    final: list[str],
    table_name: str,
    inputs: dict[str, InputDoc],
    types: list[Any],
) -> None:
    if not inputs:
        return

    final.append(f"#### {table_name}")
    final.append("| Name | Description | Type |")
    final.append("| - | - | - |")

    for name, body in inputs.items():
        final.append(f"| {name} | {body} | {_format_type(body.type, types)} |")


def markdown_docs(docs: DocsType) -> str:
    final: list[str] = ["# Docs"]
    types: list[Any] = []
    final.append(f"## Routes")

    for k, v in docs.items():
        final.append(f"### {k[0]} `{k[1]}`")
        final.append(f"*{v.desc}*")

        _make_table(final, "Query Parameters", v.query, types)
        _make_table(final, "Body Parameters", v.body, types)

    return "\n".join(final)
