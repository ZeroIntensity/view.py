from __future__ import annotations

from io import StringIO
from typing import Any, NamedTuple


class ViewNode(NamedTuple):
    name: str
    content: tuple[Any]
    attributes: dict[str, Any]

    def __str__(self):
        attrs = StringIO()

        if self.attributes:
            attrs.write(" ")

        for k, v in self.attributes.items():
            if v:
                attrs.write(f"{k}={v} ")
            else:
                attrs.write(f"{k} ")

        return (
            f"<{self.name}{attrs.getvalue()}>{''.join(self.content)}"
            f"</{self.name}>"
        )


def new_node(name: str, *content: Any, **attributes: Any) -> ViewNode:
    return ViewNode(name, content, attributes)
