from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from _typeshed import ReadableBuffer

import codecs
import encodings
import re
from dataclasses import dataclass
from encodings.utf_8 import StreamReader as UTF8StreamReader
from html.parser import HTMLParser
from io import StringIO

Input = Union[bytes, bytearray, memoryview]

UTF8 = encodings.search_function("utf-8")
assert UTF8
TAG = re.compile(r"< *([A-z]+) *(.*) *>(.*)< *\/([A-z]+) *>")


@dataclass()
class _Tag:
    name: str
    attrs: dict[str, str | None]
    content: list[str | _Tag]


@dataclass()
class _Item:
    tag: _Tag | None
    source: str | None


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._tags: list[_Tag] = []
        self.source: list[_Item] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        dict_attrs = {
            tup[0]: (repr(tup[1]) if tup[1] else None) for tup in attrs
        }
        if not self._tags:
            self._tags.append(_Tag(tag, dict_attrs, []))
        else:
            tg = _Tag(tag, dict_attrs, [])
            self._tags[-1].content.append(tg)
            self._tags.append(tg)

    def handle_endtag(self, tag: str):
        if not self._tags:
            raise SyntaxError(f'unexpected end tag "{tag}"')
        if self._tags[-1].name != tag:
            raise SyntaxError(
                f"expected end tag for {self._tags[-1].name!r}, got {tag!r}"
            )
        if len(self._tags) == 1:
            self.source.append(_Item(self._tags.pop(), None))
        else:
            self._tags.pop()

    def handle_data(self, data: str):
        if not self._tags:
            self.source.append(_Item(None, data))
        else:
            self._tags[-1].content.append(data)


def _transform_recursive(tag: _Tag) -> str:
    attrs = [f"{a}={b}" for a, b in tag.attrs.items()]
    items = []

    for i in tag.content:
        if isinstance(i, _Tag):
            items.append(_transform_recursive(i))
        elif isinstance(i, str):
            items.append(i)
        else:
            items.append("''")

    content = StringIO()

    if items:
        content.write(", ")

    for index, value in enumerate(items):
        content.write(f"{value}{', ' if (index + 1) != len(items) else ''}")

    if attrs:
        content.write(", ")

    return (
        f"_vpy_newnode({repr(tag.name)}{content.getvalue()}"
        f"{','.join(attrs)})"
    )


def _transform(code: str) -> str:
    p = _Parser()
    p.feed(code)
    source = StringIO()

    for tag in p.source:
        if tag.tag:
            source.write(_transform_recursive(tag.tag))
        else:
            assert tag.source
            source.write(tag.source)
    return (
        "from view.nodes import new_node as _vpy_newnode\n" + source.getvalue()
    )


def decode(source: Input) -> str:
    return _transform(bytes(source).decode())


def view_decode(input: bytes, errors: str = "strict") -> tuple[str, int]:
    code, length = UTF8.decode(input, errors)

    return _transform(code), length


def transform_stream(stream: Any) -> StringIO:
    return StringIO(_transform(stream.read()))


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(
        self, input: ReadableBuffer, errors: str, final: bool
    ) -> tuple[str, int]:
        if final:
            return view_decode(input, errors)  # type: ignore
        else:
            return "", 0


class StreamReader(UTF8StreamReader):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.stream: StringIO = transform_stream(self.stream)


codecs.register(
    {
        "view": codecs.CodecInfo(
            UTF8.encode,
            view_decode,
            name="view",
            streamreader=StreamReader,
            streamwriter=UTF8.streamwriter,
            incrementalencoder=UTF8.incrementalencoder,
            incrementaldecoder=IncrementalDecoder,
        )
    }.get
)
