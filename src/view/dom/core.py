from __future__ import annotations

import uuid
from collections.abc import (
    AsyncIterator,
    Callable,
    Iterator,
    MutableMapping,
    MutableSequence,
)
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from io import StringIO
from queue import LifoQueue
from typing import ClassVar, ParamSpec, TypeAlias

from view.core.headers import as_multidict
from view.core.response import Response
from view.core.router import RouteView
from view.exceptions import InvalidTypeError
from view.javascript import SupportsJavaScript

__all__ = ("HTMLNode", "html_response")

HTMLTree: TypeAlias = Iterator["HTMLNode"]


def _indent_iterator(iterator: Iterator[str]) -> Iterator[str]:
    for line in iterator:
        try:
            yield "    " + line
        except TypeError as error:
            raise TypeError(f"unexpected line: {line!r}") from error


@dataclass(slots=True)
class HTMLNode(SupportsJavaScript):
    """
    Data class representing an HTML node in the tree.
    """

    node_stack: ClassVar[ContextVar[LifoQueue[HTMLNode]]] = ContextVar("node_stack")

    node_name: str
    """
    Name of the node as it will appear in the HTML. For example, in an <html>
    node, this will be the string 'html'.
    """

    is_real: bool = True
    """
    Whether this node will actually be included in the output. Generally, most
    nodes will be rendered, but there are a few special types of nodes that
    are only used during the rendering process.
    """

    text: str = ""
    """
    The direct text of this node, not including any other children.
    """

    attributes: MutableMapping[str, str] = field(default_factory=dict)
    """
    Dictionary containing attribute names and values as they will be rendered
    in the final output.
    """

    children: MutableSequence[HTMLNode] = field(default_factory=list)
    """
    All nodes that are a direct descendant of this node.
    """

    @classmethod
    def virtual(cls, name: str) -> HTMLNode:
        """
        Create a new "fake" node.
        """

        return cls(f"__view_internal_{name}_node", is_real=False)

    @classmethod
    def new(
        cls,
        name: str,
        *,
        child_text: str | None = None,
        attributes: MutableMapping[str, str] | None = None,
    ) -> HTMLNode:
        """
        Create a new node that will be included in the final HTML.
        """
        return cls(
            name,
            is_real=True,
            text=child_text or "",
            attributes=attributes or {},
            children=[],
        )

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

        if self.is_real:
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
            assert self.attributes == {}, self.attributes
            yield from self._html_body()

    def as_html(self) -> str:
        """
        Convert this node to HTML code.
        """

        buffer = StringIO()
        for line in self.as_html_stream():
            buffer.write(line + "\n")

        return buffer.getvalue()

    def as_javascript(self) -> str:
        element_id = self.attributes.setdefault("id", uuid.uuid4().hex)
        return f"document.getElementById({element_id!r})"


@contextmanager
def html_context() -> HTMLTree:
    """
    Enter a context in which HTML nodes can be created under a fresh tree.
    """
    stack = LifoQueue()
    token = HTMLNode.node_stack.set(stack)

    tree = HTMLNode.virtual("tree_top")
    stack.put_nowait(tree)

    try:
        yield tree
    finally:
        HTMLNode.node_stack.reset(token)


P = ParamSpec("P")
HTMLViewResponseItem: TypeAlias = HTMLNode | int
HTMLViewResult = AsyncIterator[HTMLViewResponseItem] | Iterator[HTMLViewResponseItem]
HTMLView: TypeAlias = Callable[P, HTMLViewResult]


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
                    raise InvalidTypeError(iterator, AsyncIterator, Iterator)

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
