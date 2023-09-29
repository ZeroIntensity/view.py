from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .app import InputDoc
from .typing import DocsType

if TYPE_CHECKING:
    from ._loader import LoaderDoc
    from .routing import _NoDefaultType

from .routing import _NoDefault

_PRIMITIVES = {
    str: "string",
    int: "integer",
    dict: "object",
    Any: "any",
    bool: "boolean",
    float: "double",
    None: "null",
}


def _tp_name(tp: Any, types: list[Any]) -> str:
    prim = _PRIMITIVES.get(tp)
    if prim:
        return f"`{prim}`"
    else:
        if tp not in types:
            doc: dict[str, LoaderDoc] = getattr(tp, "_view_doc")
            types.append(tp)

            for v in doc.values():
                _tp_name(v.tp, types)

        return f"`{tp.__name__}`"


def _format_type(tp: tuple[type[Any], ...], types: list[Any]) -> str:
    if len(tp) == 1:
        return _tp_name(tp[0], types)

    final = ""

    for index, i in enumerate(tp):
        if (index + 1) == len(tp):
            final += _tp_name(i, types)
        else:
            final += f"{_tp_name(i, types)} | "

    return final


def _format_default(default: Any | _NoDefaultType) -> str:
    if hasattr(default, "__VIEW_NODEFAULT__"):
        return "**Required**"

    return f"`{default!r}`"


def _make_table(
    final: list[str],
    table_name: str,
    inputs: dict[str, InputDoc],
    types: list[Any],
) -> None:
    if not inputs:
        return

    final.append(f"#### {table_name}")
    final.append("| Name | Description | Type | Default |")
    final.append("| - | - | - | - |")

    for name, body in inputs.items():
        final.append(
            f"| {name} | {body.desc} | {_format_type(body.type, types)} | {_format_default(body.default)} |"  # noqa
        )


def markdown_docs(docs: DocsType) -> str:
    final: list[str] = []
    types: list[Any] = []
    final.append(f"\n## Routes")

    for k, v in docs.items():
        final.append(f"### {k[0]} `{k[1]}`")
        final.append(f"*{v.desc}*")

        _make_table(final, "Query Parameters", v.query, types)
        _make_table(final, "Body Parameters", v.body, types)

    part = ["\n## Types"]

    for i in types:
        doc: dict[str, LoaderDoc] = getattr(i, "_view_doc")
        part.append(f"### `{i.__name__}`")
        part.append("| Key | Description | Type | Default |")
        part.append("| - | - | - | - |")

        for k, v in doc.items():
            part.append(
                f"| {k} | {v.desc} | {_format_type((v.tp,), types)} | {_format_default(v.default)} |"
            )

    return "# Docs" + "\n".join(part) + "\n".join(final)
