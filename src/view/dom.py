from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from queue import LifoQueue
from typing import (
    Any,
    AsyncIterator,
    Callable,
    ClassVar,
    Iterator,
    ParamSpec,
    Protocol,
    Self,
    TypeAlias,
    TypedDict,
    Unpack,
    Literal,
    NotRequired,
)

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


def _construct_node(
    name: str,
    child_text: str | None = None,
    *,
    attributes: dict[str, Any],
    global_attributes: GlobalAttributes,
    data: dict[str, str],
) -> HTMLNode:
    if __debug__ and ((child_text is not None) and not isinstance(child_text, str)):
        raise InvalidType(str, child_text)

    attributes = {**attributes, **global_attributes}
    for name, value in data.items():
        attributes[f"data-{name}"] = value
    stack = HTMLNode.node_stack.get()
    top = stack.queue[-1]

    # Since "class" is a reserved Python keyword, we have to use cls instead
    if "cls" in attributes:
        attributes["class"] = attributes.pop("cls")

    for attribute in list(attributes.keys()):
        if "_" in attribute:
            attributes[attribute.replace("_", "-")] = str(attributes.pop(attribute))

    new_node = HTMLNode(name, child_text or "", attributes, [])
    top.children.append(new_node)
    return new_node


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

        return Response(
            stream, status_code or 200, as_multidict({"content-type": "text/html"})
        )

    return wrapper


class GlobalAttributes(TypedDict):
    accesskey: NotRequired[str]
    """Specifies a keyboard shortcut to activate or focus the element"""

    cls: NotRequired[str]
    """Specifies one or more class names for an element (refers to a class in a style sheet)"""

    contenteditable: NotRequired[Literal["true", "false", "plaintext-only"]]
    """Specifies whether the content of an element is editable or not"""

    dir: NotRequired[Literal["ltr", "rtl", "auto"]]
    """Specifies the text direction for the content in an element"""

    draggable: NotRequired[Literal["true", "false", "auto"]]
    """Specifies whether an element is draggable or not"""

    hidden: NotRequired[bool]
    """Specifies that an element is not yet, or is no longer, relevant"""

    id: NotRequired[str]
    """Specifies a unique id for an element"""

    lang: NotRequired[str]
    """Specifies the language of the element's content"""

    spellcheck: NotRequired[Literal["true", "false"]]
    """Specifies whether the element is to have its spelling and grammar checked or not"""

    style: NotRequired[str]
    """Specifies an inline CSS style for an element"""

    tabindex: NotRequired[int]
    """Specifies the tabbing order of an element"""

    title: NotRequired[str]
    """Specifies extra information about an element (displayed as a tooltip)"""

    translate: NotRequired[Literal["yes", "no"]]
    """Specifies whether the content of an element should be translated or not"""

    onabort: NotRequired[str]
    """Script to be run on abort"""

    onblur: NotRequired[str]
    """Script to be run when an element loses focus"""

    oncancel: NotRequired[str]
    """Script to be run when a dialog is canceled"""

    oncanplay: NotRequired[str]
    """Script to be run when a file is ready to start playing"""

    oncanplaythrough: NotRequired[str]
    """Script to be run when a file can be played all the way through without pausing"""

    onchange: NotRequired[str]
    """Script to be run when the value of an element is changed"""

    onclick: NotRequired[str]
    """Script to be run on a mouse click"""

    onclose: NotRequired[str]
    """Script to be run when a dialog is closed"""

    oncontextmenu: NotRequired[str]
    """Script to be run when a context menu is triggered"""

    oncopy: NotRequired[str]
    """Script to be run when the content of an element is copied"""

    oncuechange: NotRequired[str]
    """Script to be run when the cue changes in a track element"""

    oncut: NotRequired[str]
    """Script to be run when the content of an element is cut"""

    ondblclick: NotRequired[str]
    """Script to be run on a mouse double-click"""

    ondrag: NotRequired[str]
    """Script to be run when an element is dragged"""

    ondragend: NotRequired[str]
    """Script to be run at the end of a drag operation"""

    ondragenter: NotRequired[str]
    """Script to be run when an element has been dragged to a valid drop target"""

    ondragleave: NotRequired[str]
    """Script to be run when an element leaves a valid drop target"""

    ondragover: NotRequired[str]
    """Script to be run when an element is being dragged over a valid drop target"""

    ondragstart: NotRequired[str]
    """Script to be run at the start of a drag operation"""

    ondrop: NotRequired[str]
    """Script to be run when dragged element is being dropped"""

    ondurationchange: NotRequired[str]
    """Script to be run when the length of the media changes"""

    onemptied: NotRequired[str]
    """Script to be run when media resource is suddenly unavailable"""

    onended: NotRequired[str]
    """Script to be run when the media has reach the end"""

    onerror: NotRequired[str]
    """Script to be run when an error occurs"""

    onfocus: NotRequired[str]
    """Script to be run when an element gets focus"""

    oninput: NotRequired[str]
    """Script to be run when an element gets user input"""

    oninvalid: NotRequired[str]
    """Script to be run when an element is invalid"""

    onkeydown: NotRequired[str]
    """Script to be run when a user is pressing a key"""

    onkeypress: NotRequired[str]
    """Script to be run when a user presses a key"""

    onkeyup: NotRequired[str]
    """Script to be run when a user releases a key"""

    onload: NotRequired[str]
    """Script to be run when the element has finished loading"""

    onloadeddata: NotRequired[str]
    """Script to be run when media data is loaded"""

    onloadedmetadata: NotRequired[str]
    """Script to be run when meta data is loaded"""

    onloadstart: NotRequired[str]
    """Script to be run just as the file begins to load"""

    onmousedown: NotRequired[str]
    """Script to be run when a mouse button is pressed down on an element"""

    onmouseenter: NotRequired[str]
    """Script to be run when the mouse pointer enters an element"""

    onmouseleave: NotRequired[str]
    """Script to be run when the mouse pointer leaves an element"""

    onmousemove: NotRequired[str]
    """Script to be run when the mouse pointer is moving over an element"""

    onmouseout: NotRequired[str]
    """Script to be run when the mouse pointer moves out of an element"""

    onmouseover: NotRequired[str]
    """Script to be run when the mouse pointer moves over an element"""

    onmouseup: NotRequired[str]
    """Script to be run when a mouse button is released over an element"""

    onpaste: NotRequired[str]
    """Script to be run when content is pasted into an element"""

    onpause: NotRequired[str]
    """Script to be run when the media is paused"""

    onplay: NotRequired[str]
    """Script to be run when the media starts playing"""

    onplaying: NotRequired[str]
    """Script to be run when the media actually has started playing"""

    onprogress: NotRequired[str]
    """Script to be run when the browser is in the process of getting the media data"""

    onratechange: NotRequired[str]
    """Script to be run each time the playback rate changes"""

    onreset: NotRequired[str]
    """Script to be run when a form is reset"""

    onresize: NotRequired[str]
    """Script to be run when the browser window is being resized"""

    onscroll: NotRequired[str]
    """Script to be run when an element's scrollbar is being scrolled"""

    onseeked: NotRequired[str]
    """Script to be run when seeking has ended"""

    onseeking: NotRequired[str]
    """Script to be run when seeking begins"""

    onselect: NotRequired[str]
    """Script to be run when the element gets selected"""

    onshow: NotRequired[str]
    """Script to be run when a context menu is shown"""

    onstalled: NotRequired[str]
    """Script to be run when the browser is unable to fetch the media data"""

    onsubmit: NotRequired[str]
    """Script to be run when a form is submitted"""

    onsuspend: NotRequired[str]
    """Script to be run when fetching the media data is stopped"""

    ontimeupdate: NotRequired[str]
    """Script to be run when the playing position has changed"""

    ontoggle: NotRequired[str]
    """Script to be run when the user opens or closes a details element"""

    onvolumechange: NotRequired[str]
    """Script to be run each time the volume is changed"""

    onwaiting: NotRequired[str]
    """Script to be run when the media has paused but is expected to resume"""

    onwheel: NotRequired[str]
    """Script to be run when the mouse wheel rolls up or down over an element"""


def a(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    href: str | None = None,
    target: Literal["_blank", "_self", "_parent", "_top"] = "_self",
    download: str | None = None,
    rel: str | None = None,
    hreflang: str | None = None,
    type: str | None = None,
    referrerpolicy: (
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
        | None
    ) = None,
    ping: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a hyperlink that links to another page or location within the same page"""
    return _construct_node(
        "a",
        child_text=child_text,
        attributes={
            "href": href,
            "target": target,
            "download": download,
            "rel": rel,
            "hreflang": hreflang,
            "type": type,
            "referrerpolicy": referrerpolicy,
            "ping": ping,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def abbr(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines an abbreviation or acronym, optionally with its expansion"""
    return _construct_node(
        "abbr",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def address(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines contact information for the author/owner of a document or article"""
    return _construct_node(
        "address",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def span(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines an inline container with no semantic meaning, used for styling or scripting"""
    return _construct_node(
        "span",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def strong(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines important text with strong importance (typically bold)"""
    return _construct_node(
        "strong",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def style(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    media: str | None = None,
    type: str = "text/css",
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Contains style information (CSS) for a document"""
    return _construct_node(
        "style",
        child_text=child_text,
        attributes={
            "media": media,
            "type": type,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def sub(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines subscript text"""
    return _construct_node(
        "sub",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def summary(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a visible heading for a details element"""
    return _construct_node(
        "summary",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def sup(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines superscript text"""
    return _construct_node(
        "sup",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def table(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a table"""
    return _construct_node(
        "table",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def tbody(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Groups the body content in a table"""
    return _construct_node(
        "tbody",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def td(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    colspan: int = 1,
    rowspan: int = 1,
    headers: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a standard data cell in a table"""
    return _construct_node(
        "td",
        child_text=child_text,
        attributes={
            "colspan": colspan,
            "rowspan": rowspan,
            "headers": headers,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def template(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a container for content that should not be rendered when the page loads"""
    return _construct_node(
        "template",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def textarea(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    name: str | None = None,
    rows: int | None = None,
    cols: int | None = None,
    placeholder: str | None = None,
    required: bool = False,
    readonly: bool = False,
    disabled: bool = False,
    maxlength: int | None = None,
    minlength: int | None = None,
    wrap: Literal["hard", "soft"] = "soft",
    autocomplete: Literal["on", "off"] | None = None,
    autofocus: bool = False,
    form: str | None = None,
    dirname: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a multi-line text input control"""
    return _construct_node(
        "textarea",
        child_text=child_text,
        attributes={
            "name": name,
            "rows": rows,
            "cols": cols,
            "placeholder": placeholder,
            "required": required,
            "readonly": readonly,
            "disabled": disabled,
            "maxlength": maxlength,
            "minlength": minlength,
            "wrap": wrap,
            "autocomplete": autocomplete,
            "autofocus": autofocus,
            "form": form,
            "dirname": dirname,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def tfoot(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Groups the footer content in a table"""
    return _construct_node(
        "tfoot",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def th(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    colspan: int = 1,
    rowspan: int = 1,
    headers: str | None = None,
    scope: Literal["col", "row", "colgroup", "rowgroup"] | None = None,
    abbr: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a header cell in a table"""
    return _construct_node(
        "th",
        child_text=child_text,
        attributes={
            "colspan": colspan,
            "rowspan": rowspan,
            "headers": headers,
            "scope": scope,
            "abbr": abbr,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def thead(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Groups the header content in a table"""
    return _construct_node(
        "thead",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def time(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    datetime: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a specific time (or datetime)"""
    return _construct_node(
        "time",
        child_text=child_text,
        attributes={
            "datetime": datetime,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def title(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines the title of the document (shown in browser's title bar or tab)"""
    return _construct_node(
        "title",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def tr(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a row in a table"""
    return _construct_node(
        "tr",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def track(
    *,
    data: dict[str, str] | None = None,
    kind: Literal[
        "subtitles", "captions", "descriptions", "chapters", "metadata"
    ] = "subtitles",
    src: str | None,
    srclang: str | None = None,
    label: str | None = None,
    default: bool = False,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines text tracks for media elements (video and audio)"""
    return _construct_node(
        "track",
        attributes={
            "kind": kind,
            "src": src,
            "srclang": srclang,
            "label": label,
            "default": default,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def u(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines text with an unarticulated, non-textual annotation (typically underlined)"""
    return _construct_node(
        "u",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def ul(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines an unordered (bulleted) list"""
    return _construct_node(
        "ul",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def var(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a variable in programming or mathematical contexts"""
    return _construct_node(
        "var",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def video(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    src: str | None = None,
    controls: bool = False,
    width: int | None = None,
    height: int | None = None,
    autoplay: bool = False,
    loop: bool = False,
    muted: bool = False,
    preload: Literal["auto", "metadata", "none"] = "auto",
    poster: str | None = None,
    playsinline: bool = False,
    crossorigin: Literal["anonymous", "use-credentials"] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Embeds video content in the document"""
    return _construct_node(
        "video",
        child_text=child_text,
        attributes={
            "src": src,
            "controls": controls,
            "width": width,
            "height": height,
            "autoplay": autoplay,
            "loop": loop,
            "muted": muted,
            "preload": preload,
            "poster": poster,
            "playsinline": playsinline,
            "crossorigin": crossorigin,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def wbr(
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a possible line-break opportunity in text"""
    return _construct_node(
        "wbr",
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def area(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    alt: str | None,
    coords: str | None = None,
    shape: Literal["default", "rect", "circle", "poly"] = "rect",
    href: str | None = None,
    target: Literal["_blank", "_self", "_parent", "_top"] | None = None,
    download: str | None = None,
    rel: str | None = None,
    referrerpolicy: (
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
        | None
    ) = None,
    ping: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a clickable area inside an image map"""
    return _construct_node(
        "area",
        child_text=child_text,
        attributes={
            "alt": alt,
            "coords": coords,
            "shape": shape,
            "href": href,
            "target": target,
            "download": download,
            "rel": rel,
            "referrerpolicy": referrerpolicy,
            "ping": ping,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def article(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines independent, self-contained content that could be distributed independently"""
    return _construct_node(
        "article",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def aside(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines content aside from the main content (like a sidebar)"""
    return _construct_node(
        "aside",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def audio(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    src: str | None = None,
    controls: bool = False,
    autoplay: bool = False,
    loop: bool = False,
    muted: bool = False,
    preload: Literal["auto", "metadata", "none"] = "auto",
    crossorigin: Literal["anonymous", "use-credentials"] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Embeds sound content in documents"""
    return _construct_node(
        "audio",
        child_text=child_text,
        attributes={
            "src": src,
            "controls": controls,
            "autoplay": autoplay,
            "loop": loop,
            "muted": muted,
            "preload": preload,
            "crossorigin": crossorigin,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def b(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines bold text without extra importance (use <strong> for importance)"""
    return _construct_node(
        "b",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def base(
    *,
    data: dict[str, str] | None = None,
    href: str | None = None,
    target: Literal["_blank", "_self", "_parent", "_top"] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Specifies the base URL and/or target for all relative URLs in a document"""
    return _construct_node(
        "base",
        attributes={
            "href": href,
            "target": target,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def bdi(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Isolates text that might be formatted in a different direction from other text"""
    return _construct_node(
        "bdi",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def bdo(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    dir: Literal["ltr", "rtl"] | None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Overrides the current text direction"""
    return _construct_node(
        "bdo",
        child_text=child_text,
        attributes={
            "dir": dir,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def blockquote(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    cite: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a section that is quoted from another source"""
    return _construct_node(
        "blockquote",
        child_text=child_text,
        attributes={
            "cite": cite,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def body(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines the document's body, containing all visible contents"""
    return _construct_node(
        "body",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def br(
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Inserts a single line break"""
    return _construct_node(
        "br",
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def button(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    type: Literal["button", "submit", "reset"] = "submit",
    name: str | None = None,
    value: str | None = None,
    disabled: bool = False,
    form: str | None = None,
    formaction: str | None = None,
    formenctype: (
        Literal[
            "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
        ]
        | None
    ) = None,
    formmethod: Literal["get", "post"] | None = None,
    formnovalidate: bool = False,
    formtarget: Literal["_blank", "_self", "_parent", "_top"] | None = None,
    autofocus: bool = False,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a clickable button"""
    return _construct_node(
        "button",
        child_text=child_text,
        attributes={
            "type": type,
            "name": name,
            "value": value,
            "disabled": disabled,
            "form": form,
            "formaction": formaction,
            "formenctype": formenctype,
            "formmethod": formmethod,
            "formnovalidate": formnovalidate,
            "formtarget": formtarget,
            "autofocus": autofocus,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def canvas(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    width: int = 300,
    height: int = 150,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Provides a container for graphics that can be drawn using JavaScript"""
    return _construct_node(
        "canvas",
        child_text=child_text,
        attributes={
            "width": width,
            "height": height,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def caption(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a table caption"""
    return _construct_node(
        "caption",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def cite(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines the title of a creative work (book, movie, song, etc.)"""
    return _construct_node(
        "cite",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def code(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a piece of computer code"""
    return _construct_node(
        "code",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def col(
    *,
    data: dict[str, str] | None = None,
    span: int = 1,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Specifies column properties for each column within a <colgroup> element"""
    return _construct_node(
        "col",
        attributes={
            "span": span,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def colgroup(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    span: int = 1,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Specifies a group of one or more columns in a table for formatting"""
    return _construct_node(
        "colgroup",
        child_text=child_text,
        attributes={
            "span": span,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def data(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    value: str | None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Links content with a machine-readable translation"""
    return _construct_node(
        "data",
        child_text=child_text,
        attributes={
            "value": value,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def datalist(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Contains a set of <option> elements that represent predefined options for input controls"""
    return _construct_node(
        "datalist",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def dd(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a description/value of a term in a description list"""
    return _construct_node(
        "dd",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def del_(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    cite: str | None = None,
    datetime: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines text that has been deleted from a document"""
    return _construct_node(
        "del",
        child_text=child_text,
        attributes={
            "cite": cite,
            "datetime": datetime,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def details(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    open: bool = False,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines additional details that the user can view or hide"""
    return _construct_node(
        "details",
        child_text=child_text,
        attributes={
            "open": open,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def dfn(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Represents the defining instance of a term"""
    return _construct_node(
        "dfn",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def dialog(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    open: bool = False,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a dialog box or window"""
    return _construct_node(
        "dialog",
        child_text=child_text,
        attributes={
            "open": open,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def div(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a generic container for flow content with no semantic meaning"""
    return _construct_node(
        "div",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def dl(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a description list"""
    return _construct_node(
        "dl",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def dt(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a term/name in a description list"""
    return _construct_node(
        "dt",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def em(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines emphasized text (typically displayed in italic)"""
    return _construct_node(
        "em",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def embed(
    *,
    data: dict[str, str] | None = None,
    src: str | None,
    type: str | None = None,
    width: int | None = None,
    height: int | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Embeds external content at the specified point in the document"""
    return _construct_node(
        "embed",
        attributes={
            "src": src,
            "type": type,
            "width": width,
            "height": height,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def fieldset(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    disabled: bool = False,
    form: str | None = None,
    name: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Groups related elements in a form and draws a box around them"""
    return _construct_node(
        "fieldset",
        child_text=child_text,
        attributes={
            "disabled": disabled,
            "form": form,
            "name": name,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def figcaption(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a caption for a <figure> element"""
    return _construct_node(
        "figcaption",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def figure(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Specifies self-contained content, like illustrations, diagrams, photos, code listings, etc."""
    return _construct_node(
        "figure",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def footer(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a footer for a document or section"""
    return _construct_node(
        "footer",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def form(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    action: str | None = None,
    method: Literal["get", "post", "dialog"] = "get",
    enctype: Literal[
        "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
    ] = "application/x-www-form-urlencoded",
    name: str | None = None,
    target: Literal["_blank", "_self", "_parent", "_top"] | None = None,
    autocomplete: Literal["on", "off"] = "on",
    novalidate: bool = False,
    accept_charset: str | None = None,
    rel: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Creates an HTML form for user input"""
    return _construct_node(
        "form",
        child_text=child_text,
        attributes={
            "action": action,
            "method": method,
            "enctype": enctype,
            "name": name,
            "target": target,
            "autocomplete": autocomplete,
            "novalidate": novalidate,
            "accept-charset": accept_charset,
            "rel": rel,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def h1(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines the most important heading (level 1)"""
    return _construct_node(
        "h1",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def h2(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a level 2 heading"""
    return _construct_node(
        "h2",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def h3(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a level 3 heading"""
    return _construct_node(
        "h3",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def h4(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a level 4 heading"""
    return _construct_node(
        "h4",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def h5(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a level 5 heading"""
    return _construct_node(
        "h5",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def h6(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines the least important heading (level 6)"""
    return _construct_node(
        "h6",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def head(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Contains metadata and information about the document"""
    return _construct_node(
        "head",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def header(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a header for a document or section, typically containing introductory content"""
    return _construct_node(
        "header",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def hgroup(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Groups a set of h1-h6 elements when a heading has multiple levels"""
    return _construct_node(
        "hgroup",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def hr(
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a thematic break or horizontal rule in content"""
    return _construct_node(
        "hr",
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def html(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    xmlns: str = "http://www.w3.org/1999/xhtml",
    lang: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Represents the root element of an HTML document"""
    return _construct_node(
        "html",
        child_text=child_text,
        attributes={
            "xmlns": xmlns,
            "lang": lang,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def i(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines italic text, typically used for technical terms, foreign phrases, etc."""
    return _construct_node(
        "i",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def iframe(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    src: str | None = None,
    srcdoc: str | None = None,
    name: str | None = None,
    sandbox: str | None = None,
    allow: str | None = None,
    allowfullscreen: bool = False,
    width: int | None = None,
    height: int | None = None,
    referrerpolicy: (
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
        | None
    ) = None,
    loading: Literal["eager", "lazy"] = "eager",
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Embeds another HTML page within the current page"""
    return _construct_node(
        "iframe",
        child_text=child_text,
        attributes={
            "src": src,
            "srcdoc": srcdoc,
            "name": name,
            "sandbox": sandbox,
            "allow": allow,
            "allowfullscreen": allowfullscreen,
            "width": width,
            "height": height,
            "referrerpolicy": referrerpolicy,
            "loading": loading,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def img(
    *,
    data: dict[str, str] | None = None,
    src: str | None,
    alt: str | None,
    width: int | None = None,
    height: int | None = None,
    srcset: str | None = None,
    sizes: str | None = None,
    crossorigin: Literal["anonymous", "use-credentials"] | None = None,
    usemap: str | None = None,
    ismap: bool = False,
    loading: Literal["eager", "lazy"] = "eager",
    decoding: Literal["sync", "async", "auto"] = "auto",
    referrerpolicy: (
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
        | None
    ) = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Embeds an image in the document"""
    return _construct_node(
        "img",
        attributes={
            "src": src,
            "alt": alt,
            "width": width,
            "height": height,
            "srcset": srcset,
            "sizes": sizes,
            "crossorigin": crossorigin,
            "usemap": usemap,
            "ismap": ismap,
            "loading": loading,
            "decoding": decoding,
            "referrerpolicy": referrerpolicy,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def input(
    *,
    data: dict[str, str] | None = None,
    type: Literal[
        "button",
        "checkbox",
        "color",
        "date",
        "datetime-local",
        "email",
        "file",
        "hidden",
        "image",
        "month",
        "number",
        "password",
        "radio",
        "range",
        "reset",
        "search",
        "submit",
        "tel",
        "text",
        "time",
        "url",
        "week",
    ] = "text",
    name: str | None = None,
    value: str | None = None,
    placeholder: str | None = None,
    required: bool = False,
    readonly: bool = False,
    disabled: bool = False,
    checked: bool = False,
    autocomplete: (
        Literal[
            "on",
            "off",
            "name",
            "email",
            "username",
            "new-password",
            "current-password",
            "tel",
            "url",
            "street-address",
            "postal-code",
            "cc-number",
        ]
        | None
    ) = None,
    autofocus: bool = False,
    min: str | None = None,
    max: str | None = None,
    step: str | None = None,
    minlength: int | None = None,
    maxlength: int | None = None,
    pattern: str | None = None,
    size: int | None = None,
    multiple: bool = False,
    accept: str | None = None,
    src: str | None = None,
    alt: str | None = None,
    width: int | None = None,
    height: int | None = None,
    list: str | None = None,
    form: str | None = None,
    formaction: str | None = None,
    formenctype: (
        Literal[
            "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
        ]
        | None
    ) = None,
    formmethod: Literal["get", "post"] | None = None,
    formnovalidate: bool = False,
    formtarget: Literal["_blank", "_self", "_parent", "_top"] | None = None,
    capture: Literal["user", "environment"] | None = None,
    dirname: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Creates an interactive control for user input within a form"""
    return _construct_node(
        "input",
        attributes={
            "type": type,
            "name": name,
            "value": value,
            "placeholder": placeholder,
            "required": required,
            "readonly": readonly,
            "disabled": disabled,
            "checked": checked,
            "autocomplete": autocomplete,
            "autofocus": autofocus,
            "min": min,
            "max": max,
            "step": step,
            "minlength": minlength,
            "maxlength": maxlength,
            "pattern": pattern,
            "size": size,
            "multiple": multiple,
            "accept": accept,
            "src": src,
            "alt": alt,
            "width": width,
            "height": height,
            "list": list,
            "form": form,
            "formaction": formaction,
            "formenctype": formenctype,
            "formmethod": formmethod,
            "formnovalidate": formnovalidate,
            "formtarget": formtarget,
            "capture": capture,
            "dirname": dirname,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def ins(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    cite: str | None = None,
    datetime: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines text that has been inserted into a document"""
    return _construct_node(
        "ins",
        child_text=child_text,
        attributes={
            "cite": cite,
            "datetime": datetime,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def kbd(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines keyboard input"""
    return _construct_node(
        "kbd",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def label(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    for_: str | None = None,
    form: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a label for an input element"""
    return _construct_node(
        "label",
        child_text=child_text,
        attributes={
            "for": for_,
            "form": form,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def legend(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a caption for a fieldset element"""
    return _construct_node(
        "legend",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def li(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    value: int | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a list item"""
    return _construct_node(
        "li",
        child_text=child_text,
        attributes={
            "value": value,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def link(
    *,
    data: dict[str, str] | None = None,
    href: str | None,
    rel: str | None,
    type: str | None = None,
    media: str | None = None,
    hreflang: str | None = None,
    sizes: str | None = None,
    crossorigin: Literal["anonymous", "use-credentials"] | None = None,
    referrerpolicy: (
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
        | None
    ) = None,
    integrity: str | None = None,
    as_: (
        Literal[
            "audio",
            "document",
            "embed",
            "fetch",
            "font",
            "image",
            "object",
            "script",
            "style",
            "track",
            "video",
            "worker",
        ]
        | None
    ) = None,
    disabled: bool = False,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines the relationship between the current document and an external resource"""
    return _construct_node(
        "link",
        attributes={
            "href": href,
            "rel": rel,
            "type": type,
            "media": media,
            "hreflang": hreflang,
            "sizes": sizes,
            "crossorigin": crossorigin,
            "referrerpolicy": referrerpolicy,
            "integrity": integrity,
            "as": as_,
            "disabled": disabled,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def main(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Specifies the main content of the document"""
    return _construct_node(
        "main",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def map(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    name: str | None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a client-side image map"""
    return _construct_node(
        "map",
        child_text=child_text,
        attributes={
            "name": name,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def mark(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines marked/highlighted text"""
    return _construct_node(
        "mark",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def meta(
    *,
    data: dict[str, str] | None = None,
    name: str | None = None,
    content: str | None = None,
    charset: str | None = None,
    http_equiv: (
        Literal["content-security-policy", "content-type", "default-style", "refresh"]
        | None
    ) = None,
    property: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Provides metadata about the HTML document"""
    return _construct_node(
        "meta",
        attributes={
            "name": name,
            "content": content,
            "charset": charset,
            "http-equiv": http_equiv,
            "property": property,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def meter(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    value: int | None,
    min: int = 0,
    max: int = 1,
    low: int | None = None,
    high: int | None = None,
    optimum: int | None = None,
    form: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a scalar measurement within a known range (a gauge)"""
    return _construct_node(
        "meter",
        child_text=child_text,
        attributes={
            "value": value,
            "min": min,
            "max": max,
            "low": low,
            "high": high,
            "optimum": optimum,
            "form": form,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def nav(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a section of navigation links"""
    return _construct_node(
        "nav",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def noscript(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines alternate content for users that have disabled scripts or don't support scripting"""
    return _construct_node(
        "noscript",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def object(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    data_: str | None = None,
    type: str | None = None,
    name: str | None = None,
    usemap: str | None = None,
    form: str | None = None,
    width: int | None = None,
    height: int | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Embeds an external resource such as an image, video, audio, PDF, or Flash"""
    return _construct_node(
        "object",
        child_text=child_text,
        attributes={
            "data": data_,
            "type": type,
            "name": name,
            "usemap": usemap,
            "form": form,
            "width": width,
            "height": height,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def ol(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    reversed: bool = False,
    start: int | None = None,
    type: Literal["1", "A", "a", "I", "i"] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines an ordered (numbered) list"""
    return _construct_node(
        "ol",
        child_text=child_text,
        attributes={
            "reversed": reversed,
            "start": start,
            "type": type,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def optgroup(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    label: str | None,
    disabled: bool = False,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Groups related options in a drop-down list"""
    return _construct_node(
        "optgroup",
        child_text=child_text,
        attributes={
            "label": label,
            "disabled": disabled,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def option(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    value: str | None = None,
    label: str | None = None,
    selected: bool = False,
    disabled: bool = False,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines an option in a drop-down list"""
    return _construct_node(
        "option",
        child_text=child_text,
        attributes={
            "value": value,
            "label": label,
            "selected": selected,
            "disabled": disabled,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def output(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    for_: str | None = None,
    form: str | None = None,
    name: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Represents the result of a calculation or user action"""
    return _construct_node(
        "output",
        child_text=child_text,
        attributes={
            "for": for_,
            "form": form,
            "name": name,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def p(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a paragraph"""
    return _construct_node(
        "p",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def param(
    *,
    data: dict[str, str] | None = None,
    name: str | None,
    value: str | None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines parameters for an object element"""
    return _construct_node(
        "param",
        attributes={
            "name": name,
            "value": value,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def picture(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Contains multiple image sources, allowing for different images in different scenarios"""
    return _construct_node(
        "picture",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def pre(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines preformatted text that preserves spaces and line breaks"""
    return _construct_node(
        "pre",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def progress(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    value: int | None = None,
    max: int = 1,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Represents the progress of a task"""
    return _construct_node(
        "progress",
        child_text=child_text,
        attributes={
            "value": value,
            "max": max,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def q(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    cite: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a short inline quotation"""
    return _construct_node(
        "q",
        child_text=child_text,
        attributes={
            "cite": cite,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def rp(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines what to show in browsers that do not support ruby annotations"""
    return _construct_node(
        "rp",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def rt(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines an explanation/pronunciation of characters (for East Asian typography)"""
    return _construct_node(
        "rt",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def ruby(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a ruby annotation (for East Asian typography)"""
    return _construct_node(
        "ruby",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def s(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines text that is no longer correct or relevant (strikethrough)"""
    return _construct_node(
        "s",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def samp(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines sample output from a computer program"""
    return _construct_node(
        "samp",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def script(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    src: str | None = None,
    type: str = "text/javascript",
    async_: bool = False,
    defer: bool = False,
    crossorigin: Literal["anonymous", "use-credentials"] | None = None,
    integrity: str | None = None,
    referrerpolicy: (
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
        | None
    ) = None,
    nomodule: bool = False,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Embeds or references executable code, typically JavaScript"""
    return _construct_node(
        "script",
        child_text=child_text,
        attributes={
            "src": src,
            "type": type,
            "async": async_,
            "defer": defer,
            "crossorigin": crossorigin,
            "integrity": integrity,
            "referrerpolicy": referrerpolicy,
            "nomodule": nomodule,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def section(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a thematic grouping of content, typically with a heading"""
    return _construct_node(
        "section",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )


def select(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    name: str | None = None,
    multiple: bool = False,
    required: bool = False,
    disabled: bool = False,
    size: int | None = None,
    autofocus: bool = False,
    form: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Creates a drop-down list"""
    return _construct_node(
        "select",
        child_text=child_text,
        attributes={
            "name": name,
            "multiple": multiple,
            "required": required,
            "disabled": disabled,
            "size": size,
            "autofocus": autofocus,
            "form": form,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def slot(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    name: str | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines a slot in a web component that can be filled with markup"""
    return _construct_node(
        "slot",
        child_text=child_text,
        attributes={
            "name": name,
        },
        global_attributes=global_attributes,
        data=data or {},
    )


def small(
    child_text: str = "",
    /,
    *,
    data: dict[str, str] | None = None,
    **global_attributes: Unpack[GlobalAttributes],
) -> HTMLNode:
    """Defines smaller text (like copyright and other side-comments)"""
    return _construct_node(
        "small",
        child_text=child_text,
        attributes={},
        global_attributes=global_attributes,
        data=data or {},
    )
