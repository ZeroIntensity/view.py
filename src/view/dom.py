from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from queue import LifoQueue
from typing import (AsyncIterator, Callable, ClassVar, Iterator, ParamSpec,
                    Protocol, Self, TypeAlias)

from view.exceptions import InvalidType
from view.headers import as_multidict
from view.response import Response
from view.router import RouteView


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

    def __enter__(self) -> Self:
        stack = self.node_stack.get()
        stack.put_nowait(self)
        return self

    def __exit__(self, *_) -> None:
        stack = self.node_stack.get()
        popped = stack.get_nowait()
        assert popped is self

    def _html_body(self) -> Iterator[str]:
        if self.text != "":
            yield self.text

        for child in self.children:
            yield from child.as_html()

    def as_html(self) -> Iterator[str]:
        """
        Convert this node to actual HTML code.
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


class HTMLNodeConstructor(Protocol):
    def __call__(self, text: str = "", /, **attributes: str) -> HTMLNode: ...


def _construct_node(name: str, text: str = "", **attributes: str) -> HTMLNode:
    if __debug__ and not isinstance(text, str):
        raise InvalidType(str, text)

    stack = HTMLNode.node_stack.get()
    top = stack.queue[-1]
    # Since "class" is a reserved Python keyword, we have to use cls instead
    if "cls" in attributes:
        attributes["class"] = attributes.pop("cls")

    for attribute in list(attributes.keys()):
        if "_" in attribute:
            attributes[attribute.replace("_", "-")] = attributes.pop(attribute)

    new_node = HTMLNode(name, text, attributes, [])
    top.children.append(new_node)
    return new_node


def html(text: str = "", **attributes: str) -> HTMLNode:
    return _construct_node("html", text, **attributes)


P = ParamSpec("P")
HTMLViewResponseItem: TypeAlias = HTMLNode | int
HTMLView: TypeAlias = Callable[P, AsyncIterator[HTMLViewResponseItem] | Iterator[HTMLViewResponseItem]]


def html_response(
    function: HTMLView,
) -> RouteView:
    """
    Return a `Response` object from a function returning HTML.
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Response:
        stack = LifoQueue()
        HTMLNode.node_stack.set(stack)

        # Special top-level node that won't be included in the output
        special = HTMLNode("")
        stack.put_nowait(special)

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
            for line in special.as_html():
                yield line.encode("utf-8") + b"\n"

        return Response(stream, status_code or 200, as_multidict({"content-type": "text/html"}))

    return wrapper
