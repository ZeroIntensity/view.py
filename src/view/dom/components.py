"""
Implementation of "components" -- DOM nodes defined by the user.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, NoReturn, ParamSpec

from view.dom.core import HTMLNode, HTMLTree
from view.dom.css import Stylesheet, rule, stylesheet
from view.dom.primitives import (
    a,
    base,
    body,
    h1,
    head,
    html,
    link,
    main,
    meta,
    nav,
    p,
    script,
    style,
)
from view.dom.primitives import title as title_node

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from view.dom.css import CSSRule

__all__ = "Children", "Component", "component", "page", "welcome_page"


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
    stylesheets: Iterable[str | Stylesheet] | None = None,
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
        with head():
            yield meta(charset="utf-8")
            yield meta(
                name="viewport",
                content="width=device-width, initial-scale=1.0",
            )

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
                if isinstance(stylesheet, Stylesheet):
                    # HTML raw-text elements recognize closing tags even in
                    # CSS strings and comments. A CSS escape preserves '<'.
                    css = re.sub(
                        r"</style",
                        lambda match: r"\3c " + match.group()[1:],
                        stylesheet.as_css(),
                        flags=re.IGNORECASE,
                    )
                    yield style(css)
                else:
                    yield link(rel="stylesheet", href=stylesheet)

            yield title_node(title)
            for script_url in scripts or []:
                yield script(src=script_url, defer=True)
        with body():
            yield Children()


@stylesheet
def _welcome_styles() -> Iterable[CSSRule]:
    yield rule("body", margin=0)
    yield rule(
        ".view-welcome",
        min_height="100svh",
        box_sizing="border-box",
        padding="2rem",
        display="flex",
        flex_direction="column",
        align_items="center",
        justify_content="center",
        background="#f8fafc",
        color="#152338",
        font_family="system-ui, sans-serif",
        text_align="center",
    )
    yield rule(
        ".view-welcome h1",
        margin=0,
        font_size="clamp(3rem, 10vw, 5rem)",
        font_weight=750,
        letter_spacing="-0.07em",
    )
    yield rule(
        ".view-welcome p",
        margin="0.75rem 0 2rem",
        color="#637186",
    )
    yield rule(
        ".view-welcome nav",
        display="flex",
        flex_wrap="wrap",
        justify_content="center",
        gap="0.75rem",
    )
    yield rule(
        ".view-welcome a",
        display="inline-flex",
        align_items="center",
        justify_content="center",
        min_width="112px",
        min_height="44px",
        box_sizing="border-box",
        padding="0.65rem 1.25rem",
        border="1px solid #dbe4ef",
        border_radius="10px",
        background="#fff",
        color="#152338",
        font_size="0.875rem",
        font_weight=600,
        text_decoration="none",
        box_shadow="0 2px 4px #15233808",
        transition="background 150ms ease, box-shadow 150ms ease",
    )
    yield rule(
        ".view-welcome a.view-welcome-docs",
        border_color="#205bda",
        background="#205bda",
        color="#fff",
    )
    yield rule(
        ".view-welcome a:hover",
        box_shadow="0 4px 12px #15233818",
        background="#eef2f7",
    )
    yield rule(
        ".view-welcome a.view-welcome-docs:hover",
        border_color="#194bb7",
        background="#194bb7",
    )
    yield rule(
        ".view-welcome a:focus-visible",
        outline="2px solid #205bda",
        outline_offset="5px",
    )


@component
def welcome_page() -> HTMLTree:
    with page("view.py", stylesheets=[_welcome_styles]):
        with main(cls="view-welcome"):
            yield h1("view.py")
            yield p("Your app is running!")
            with nav():
                yield a(
                    "GitHub", href="https://github.com/ZeroIntensity/view.py"
                )
                yield a(
                    "Docs",
                    href="https://view.zintensity.dev",
                    cls="view-welcome-docs",
                )
            yield Children()
