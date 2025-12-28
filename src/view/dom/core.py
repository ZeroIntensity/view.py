from __future__ import annotations
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps
from typing import (
    Iterator,
    ClassVar,
    AsyncIterator,
    ParamSpec,
    Callable,
    TypeAlias,
)
from queue import LifoQueue
from io import StringIO
from contextlib import contextmanager

from view.headers import as_multidict
from view.router import RouteView
from view.response import Response
from view.exceptions import InvalidType

__all__ = ("HTMLNode",)


def _indent_iterator(iterator: Iterator[str]) -> Iterator[str]:
    for line in iterator:
        try:
            yield "    " + line
        except TypeError as error:
            raise TypeError(f"unexpected line: {line!r}") from error


@dataclass(slots=True)
class HTMLNode:
    """
    Data class representing an HTML node in the tree.
    """

    node_stack: ClassVar[ContextVar[LifoQueue[HTMLNode]]] = ContextVar("node_stack")

    node_name: str
    text: str = ""
    attributes: dict[str, str] = field(default_factory=dict)
    children: list[HTMLNode] = field(default_factory=list)

    def __enter__(self) -> None:
        stack = self.node_stack.get()
        stack.put_nowait(self)

    def __exit__(self, *_) -> None:
        stack = self.node_stack.get()
        popped = stack.get_nowait()
        assert popped is self, popped

    def _html_body(self) -> Iterator[str]:
        if self.text != "":
            yield self.text

        for child in self.children:
            yield from child.as_html_stream()

    def as_html_stream(self) -> Iterator[str]:
        """
        Convert this node to actual HTML code, streaming each line individually.
        """

        if self.node_name != "":
            if self.attributes == {}:
                yield f"<{self.node_name}>"
            else:
                yield f"<{self.node_name}"
                for name, value in self.attributes.items():
                    yield f'    {name}="{value}"'
                yield ">"
            yield from _indent_iterator(self._html_body())
            yield f"</{self.node_name}>"
        else:
            assert self.attributes == {}
            yield from self._html_body()

    def as_html(self) -> str:
        """
        Convert this node to HTML code.
        """

        buffer = StringIO()
        for line in self.as_html_stream():
            buffer.write(line + "\n")

        return buffer.getvalue()


class Children(HTMLNode):
    def __init__(self) -> None:
        super().__init__("_children_node")

    def __enter__(self):
        raise RuntimeError("Children() cannot be used in a 'with' block")


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
                capture_node = HTMLNode("_node_capture")
                stack.put_nowait(capture_node)
                return

    def __exit__(self, *_) -> None:
        stack = HTMLNode.node_stack.get()
        capture_node = stack.get_nowait()
        assert capture_node.node_name == "_node_capture"

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


@contextmanager
def html_context() -> Iterator[HTMLNode]:
    """
    Enter a context in which HTML nodes can be created under a fresh tree.
    """
    stack = LifoQueue()
    token = HTMLNode.node_stack.set(stack)

    # Special top-level node that won't be included in the output
    # TODO: Is this too hacky?
    special = HTMLNode("")
    stack.put_nowait(special)

    try:
        yield special
    finally:
        HTMLNode.node_stack.reset(token)


P = ParamSpec("P")
HTMLViewResponseItem: TypeAlias = HTMLNode | int
HTMLView: TypeAlias = Callable[
    P, AsyncIterator[HTMLViewResponseItem] | Iterator[HTMLViewResponseItem]
]


def html_response(
    function: HTMLView,
) -> RouteView:
    """
    Return a `Response` object from a function returning HTML.
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Response:
        with html_context() as parent:
            iterator = function(*args, **kwargs)
            status_code: int | None = None

            def try_item(item: HTMLViewResponseItem) -> None:
                nonlocal status_code

                if isinstance(item, int):
                    if __debug__ and status_code is not None:
                        raise RuntimeError("Status code was already set")
                    status_code = item

            if isinstance(iterator, AsyncIterator):
                async for item in iterator:
                    try_item(item)
            else:
                if __debug__ and not isinstance(iterator, Iterator):
                    raise InvalidType((AsyncIterator, Iterator), iterator)

                for item in iterator:
                    try_item(item)

            async def stream() -> AsyncIterator[bytes]:
                yield b"<!DOCTYPE html>\n"
                for line in parent.as_html_stream():
                    yield line.encode("utf-8") + b"\n"

        return Response(
            stream, status_code or 200, as_multidict({"content-type": "text/html"})
        )

    return wrapper
