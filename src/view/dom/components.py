from view.dom.core import HTMLNode, HTMLTree
from view.dom.primitives import html, meta, title as title_node, body, script

from typing import NoReturn, Callable, ParamSpec
from dataclasses import dataclass
from functools import wraps

__all__ = "Children", "Component", "component"


class Children(HTMLNode):
    """
    Sentinel class marking where to inject the body in a component.
    """

    def __init__(self) -> None:
        super().__init__("_children_node", is_real=False)

    def __enter__(self) -> NoReturn:
        raise RuntimeError("Children() cannot be used in a 'with' block")

    def as_html(self) -> str:
        raise RuntimeError(
            "Children() cannot be turned into HTML -- this is likely a bug with view.py"
        )


@dataclass(frozen=True)
class Component:
    """
    A node with an "injectable" body.
    """

    generator: HTMLTree

    def __enter__(self) -> None:
        stack = HTMLNode.node_stack.get()
        for node in self.generator:
            if isinstance(node, Children):
                capture_node = HTMLNode.virtual("capture")
                stack.put_nowait(capture_node)
                return

    def __exit__(self, *_) -> None:
        stack = HTMLNode.node_stack.get()
        capture_node = stack.get_nowait()
        assert not capture_node.is_real

        parent_node = stack.queue[-1]
        parent_node.children.extend(capture_node.children)

        for node in self.generator:
            if __debug__ and isinstance(node, Children):
                raise RuntimeError(
                    "Cannot use Children() multiple times for the same component"
                )


P = ParamSpec("P")


def component(function: Callable[P, HTMLTree]) -> Callable[P, Component]:
    """
    Make a function usable as an HTML node.
    """

    @wraps(function)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Component:
        return Component(function(*args, **kwargs))

    return inner


@component
def page(
    title: str, *, language: str = "en", scripts: list[str] | None = []
) -> HTMLTree:
    """
    Common layout for an HTML page.
    """
    with html(lang=language):
        yield meta(charset="utf-8")
        yield title_node(title)
        for script_url in scripts or []:
            yield script(src=script_url)
    with body():
        yield Children()
