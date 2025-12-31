from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, NoReturn, ParamSpec

from view.dom.core import HTMLNode, HTMLTree
from view.dom.primitives import base, body, html, link, meta, script
from view.dom.primitives import title as title_node

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

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


@dataclass(slots=True, frozen=True)
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
    title: str,
    *,
    language: str = "en",
    stylesheets: Iterable[str] | None = None,
    scripts: Iterable[str] | None = [],
    description: str | None = None,
    keywords: Iterable[str] | None = None,
    author: str | None = None,
    page_url: str | None = None,
) -> HTMLTree:
    """
    Common layout for an HTML page.
    """
    with html(lang=language):
        yield meta(charset="utf-8")
        yield meta(name="viewport", content="width=device-width, initial-scale=1.0")

        if description is not None:
            yield meta(name="description", content=description)

        if keywords is not None:
            yield meta(name="keywords", content=",".join(keywords))

        if author is not None:
            yield meta(name="author", content=author)

        if page_url is not None:
            yield link(rel="canonical", href=page_url)
            yield base(href=page_url)

        for stylesheet in stylesheets or []:
            yield link(rel="stylesheet", href=stylesheet)

        yield title_node(title)
        for script_url in scripts or []:
            yield script(src=script_url, defer=True)
    with body():
        yield Children()
