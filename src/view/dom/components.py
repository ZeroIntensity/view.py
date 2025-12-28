from view.dom.core import HTMLNode
from typing import NoReturn, Iterator, Callable
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

    generator: Iterator[HTMLNode]

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


def component(function: Callable[[], Iterator[HTMLNode]]) -> Callable[[], Component]:
    @wraps(function)
    def inner() -> Component:
        return Component(function())

    return inner
