from __future__ import annotations

from typing import Any, Literal

from typing_extensions import (
    NotRequired,
    TypedDict,
    Unpack,
)


class DOMNode:
    def __init__(self, data: str | DOMNode) -> None:
        self.data = str(data)
        self.compiler_ready = False

    def __str__(self) -> str:
        return self.data

    def __repr__(self) -> str:
        return f"DOMNode({self.data!r})"

    __view_result__ = __str__


AutoCapitalizeType = Literal[
    "off", "none", "on", "sentences", "words", "characters"
]
DirType = Literal["ltr", "rtl", "auto"]


class GlobalAttributes(TypedDict):
    accesskey: NotRequired[str]
    autocapitalize: NotRequired[AutoCapitalizeType]
    autofocus: NotRequired[bool]
    cls: NotRequired[str]
    contenteditable: NotRequired[bool]
    contextmenu: NotRequired[str]
    # data
    dir: NotRequired[DirType]
    draggable: NotRequired[bool]
    enterkeyhint: NotRequired[str]
    exportparts: NotRequired[str]


NEWLINE = "\n"


def _node(
    name: str,
    text: tuple[str | DOMNode],
    attrs: dict[str, Any],
    kwargs: GlobalAttributes,
) -> DOMNode:
    attributes: dict[str, str | None] = {**kwargs, **attrs}

    cls = kwargs.get("cls")
    if cls:
        attributes["class"] = cls
        kwargs.pop("cls")
        attributes.pop("cls")
    for k, v in kwargs.items():
        if isinstance(v, bool):
            attributes[k] = "true" if v else "false"
    attr_str = ""

    for k, v in attributes.items():
        if v is None:
            continue

        k = k.replace("_", "-")
        if v:
            attr_str += f" {k}={v!r}"
        else:
            attr_str += f" {k}"
    return DOMNode(
        f"<{name}{attr_str}>{NEWLINE.join([str(i) for i in text])}</{name}>",
    )


def a(
    *__content: str | DOMNode,
    download: str | None = None,
    href: str | None = None,
    hreflang: str | None = None,
    ping: str | None = None,
    referrerpolicy: str | None = None,
    rel: str | None = None,
    target: str | None = None,
    type: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "a",
        __content,
        {
            "download": download,
            "href": href,
            "hreflang": hreflang,
            "ping": ping,
            "referrerpolicy": referrerpolicy,
            "rel": rel,
            "target": target,
            "type": type,
        },
        kwargs,
    )


def abbr(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("abbr", __content, {}, kwargs)


def acronym(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("acronym", __content, {}, kwargs)


def address(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("address", __content, {}, kwargs)


def area(
    *__content: str | DOMNode,
    alt: str | None = None,
    coords: str | None = None,
    download: str | None = None,
    href: str | None = None,
    hreflang: str | None = None,
    ping: str | None = None,
    referrerpolicy: str | None = None,
    rel: str | None = None,
    shape: str | None = None,
    target: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "area",
        __content,
        {
            "alt": alt,
            "coords": coords,
            "download": download,
            "href": href,
            "hreflang": hreflang,
            "ping": ping,
            "referrerpolicy": referrerpolicy,
            "rel": rel,
            "shape": shape,
            "target": target,
        },
        kwargs,
    )


def article(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("article", __content, {}, kwargs)


def aside(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("aside", __content, {}, kwargs)


def audio(
    *__content: str | DOMNode,
    autoplay: str | None = None,
    controls: str | None = None,
    controlslist: str | None = None,
    crossorigin: str | None = None,
    disableremoteplayback: str | None = None,
    loop: str | None = None,
    muted: str | None = None,
    preload: str | None = None,
    src: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "audio",
        __content,
        {
            "autoplay": autoplay,
            "controls": controls,
            "controlslist": controlslist,
            "crossorigin": crossorigin,
            "disableremoteplayback": disableremoteplayback,
            "loop": loop,
            "muted": muted,
            "preload": preload,
            "src": src,
        },
        kwargs,
    )


def b(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("b", __content, {}, kwargs)


def base(
    *__content: str | DOMNode,
    href: str | None = None,
    target: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "base",
        __content,
        {
            "href": href,
            "target": target,
        },
        kwargs,
    )


def bdi(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("bdi", __content, {}, kwargs)


def bdo(
    *__content: str | DOMNode,
    dir: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "bdo",
        __content,
        {
            "dir": dir,
        },
        kwargs,
    )


def big(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("big", __content, {}, kwargs)


def blockquote(
    *__content: str | DOMNode,
    cite: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "blockquote",
        __content,
        {
            "cite": cite,
        },
        kwargs,
    )


def body(
    *__content: str | DOMNode,
    alink: str | None = None,
    background: str | None = None,
    bgcolor: str | None = None,
    bottommargin: str | None = None,
    leftmargin: str | None = None,
    link: str | None = None,
    onafterprint: str | None = None,
    onbeforeprint: str | None = None,
    onbeforeunload: str | None = None,
    onblur: str | None = None,
    onerror: str | None = None,
    onfocus: str | None = None,
    onhashchange: str | None = None,
    onlanguagechange: str | None = None,
    onload: str | None = None,
    onmessage: str | None = None,
    onoffline: str | None = None,
    ononline: str | None = None,
    onpopstate: str | None = None,
    onredo: str | None = None,
    onresize: str | None = None,
    onstorage: str | None = None,
    onundo: str | None = None,
    onunload: str | None = None,
    rightmargin: str | None = None,
    text: str | None = None,
    topmargin: str | None = None,
    vlink: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "body",
        __content,
        {
            "alink": alink,
            "background": background,
            "bgcolor": bgcolor,
            "bottommargin": bottommargin,
            "leftmargin": leftmargin,
            "link": link,
            "onafterprint": onafterprint,
            "onbeforeprint": onbeforeprint,
            "onbeforeunload": onbeforeunload,
            "onblur": onblur,
            "onerror": onerror,
            "onfocus": onfocus,
            "onhashchange": onhashchange,
            "onlanguagechange": onlanguagechange,
            "onload": onload,
            "onmessage": onmessage,
            "onoffline": onoffline,
            "ononline": ononline,
            "onpopstate": onpopstate,
            "onredo": onredo,
            "onresize": onresize,
            "onstorage": onstorage,
            "onundo": onundo,
            "onunload": onunload,
            "rightmargin": rightmargin,
            "text": text,
            "topmargin": topmargin,
            "vlink": vlink,
        },
        kwargs,
    )


def br(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("br", __content, {}, kwargs)


def button(
    *__content: str | DOMNode,
    autofocus: str | None = None,
    autocomplete: str | None = None,
    disabled: str | None = None,
    form: str | None = None,
    formaction: str | None = None,
    formenctype: str | None = None,
    formmethod: str | None = None,
    formnovalidate: str | None = None,
    formtarget: str | None = None,
    name: str | None = None,
    popovertarget: str | None = None,
    popovertargetaction: str | None = None,
    type: str | None = None,
    value: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "button",
        __content,
        {
            "autofocus": autofocus,
            "autocomplete": autocomplete,
            "disabled": disabled,
            "form": form,
            "formaction": formaction,
            "formenctype": formenctype,
            "formmethod": formmethod,
            "formnovalidate": formnovalidate,
            "formtarget": formtarget,
            "name": name,
            "popovertarget": popovertarget,
            "popovertargetaction": popovertargetaction,
            "type": type,
            "value": value,
        },
        kwargs,
    )


def canvas(
    *__content: str | DOMNode,
    height: str | None = None,
    moz_opaque: str | None = None,
    width: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "canvas",
        __content,
        {
            "height": height,
            "moz_opaque": moz_opaque,
            "width": width,
        },
        kwargs,
    )


def caption(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("caption", __content, {}, kwargs)


def center(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("center", __content, {}, kwargs)


def cite(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("cite", __content, {}, kwargs)


def code(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("code", __content, {}, kwargs)


def col(
    *__content: str | DOMNode,
    span: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "col",
        __content,
        {
            "span": span,
        },
        kwargs,
    )


def colgroup(
    *__content: str | DOMNode,
    span: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "colgroup",
        __content,
        {
            "span": span,
        },
        kwargs,
    )


def data(
    *__content: str | DOMNode,
    value: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "data",
        __content,
        {
            "value": value,
        },
        kwargs,
    )


def datalist(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("datalist", __content, {}, kwargs)


def dd(
    *__content: str | DOMNode,
    nowrap: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "dd",
        __content,
        {
            "nowrap": nowrap,
        },
        kwargs,
    )


def html_del(
    *__content: str | DOMNode,
    cite: str | None = None,
    datetime: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "html_del",
        __content,
        {
            "cite": cite,
            "datetime": datetime,
        },
        kwargs,
    )


def details(
    *__content: str | DOMNode,
    open: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "details",
        __content,
        {
            "open": open,
        },
        kwargs,
    )


def dfn(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("dfn", __content, {}, kwargs)


def dialog(
    *__content: str | DOMNode,
    open: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "dialog",
        __content,
        {
            "open": open,
        },
        kwargs,
    )


def dir(
    *__content: str | DOMNode,
    compact: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "dir",
        __content,
        {
            "compact": compact,
        },
        kwargs,
    )


def div(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("div", __content, {}, kwargs)


def dl(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("dl", __content, {}, kwargs)


def dt(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("dt", __content, {}, kwargs)


def em(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("em", __content, {}, kwargs)


def embed(
    *__content: str | DOMNode,
    height: str | None = None,
    src: str | None = None,
    type: str | None = None,
    width: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "embed",
        __content,
        {
            "height": height,
            "src": src,
            "type": type,
            "width": width,
        },
        kwargs,
    )


def fieldset(
    *__content: str | DOMNode,
    disabled: str | None = None,
    form: str | None = None,
    name: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "fieldset",
        __content,
        {
            "disabled": disabled,
            "form": form,
            "name": name,
        },
        kwargs,
    )


def figcaption(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("figcaption", __content, {}, kwargs)


def figure(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("figure", __content, {}, kwargs)


def font(
    *__content: str | DOMNode,
    color: str | None = None,
    face: str | None = None,
    size: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "font",
        __content,
        {
            "color": color,
            "face": face,
            "size": size,
        },
        kwargs,
    )


def footer(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("footer", __content, {}, kwargs)


def form(
    *__content: str | DOMNode,
    accept: str | None = None,
    accept_charset: str | None = None,
    autocapitalize: str | None = None,
    autocomplete: str | None = None,
    name: str | None = None,
    rel: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "form",
        __content,
        {
            "accept": accept,
            "accept_charset": accept_charset,
            "autocapitalize": autocapitalize,
            "autocomplete": autocomplete,
            "name": name,
            "rel": rel,
        },
        kwargs,
    )


def frame(
    *__content: str | DOMNode,
    src: str | None = None,
    name: str | None = None,
    noresize: str | None = None,
    scrolling: str | None = None,
    marginheight: str | None = None,
    marginwidth: str | None = None,
    frameborder: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "frame",
        __content,
        {
            "src": src,
            "name": name,
            "noresize": noresize,
            "scrolling": scrolling,
            "marginheight": marginheight,
            "marginwidth": marginwidth,
            "frameborder": frameborder,
        },
        kwargs,
    )


def frameset(
    *__content: str | DOMNode,
    cols: str | None = None,
    rows: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "frameset",
        __content,
        {
            "cols": cols,
            "rows": rows,
        },
        kwargs,
    )


def h1(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("h1", __content, {}, kwargs)


def h2(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("h2", __content, {}, kwargs)


def h3(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("h3", __content, {}, kwargs)


def h4(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("h4", __content, {}, kwargs)


def h5(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("h5", __content, {}, kwargs)


def h6(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("h6", __content, {}, kwargs)


def head(
    *__content: str | DOMNode,
    profile: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "head",
        __content,
        {
            "profile": profile,
        },
        kwargs,
    )


def header(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("header", __content, {}, kwargs)


def hgroup(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("hgroup", __content, {}, kwargs)


def hr(
    *__content: str | DOMNode,
    align: str | None = None,
    color: str | None = None,
    noshade: str | None = None,
    size: str | None = None,
    width: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "hr",
        __content,
        {
            "align": align,
            "color": color,
            "noshade": noshade,
            "size": size,
            "width": width,
        },
        kwargs,
    )


def html(
    *__content: str | DOMNode,
    manifest: str | None = None,
    version: str | None = None,
    xmlns: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "html",
        __content,
        {
            "manifest": manifest,
            "version": version,
            "xmlns": xmlns,
        },
        kwargs,
    )


def i(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("i", __content, {}, kwargs)


def iframe(
    *__content: str | DOMNode,
    allow: str | None = None,
    allowfullscreen: str | None = None,
    allowpaymentrequest: str | None = None,
    credentialless: str | None = None,
    csp: str | None = None,
    height: str | None = None,
    loading: str | None = None,
    name: str | None = None,
    referrerpolicy: str | None = None,
    sandbox: str | None = None,
    src: str | None = None,
    srcdoc: str | None = None,
    width: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "iframe",
        __content,
        {
            "allow": allow,
            "allowfullscreen": allowfullscreen,
            "allowpaymentrequest": allowpaymentrequest,
            "credentialless": credentialless,
            "csp": csp,
            "height": height,
            "loading": loading,
            "name": name,
            "referrerpolicy": referrerpolicy,
            "sandbox": sandbox,
            "src": src,
            "srcdoc": srcdoc,
            "width": width,
        },
        kwargs,
    )


def image(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("image", __content, {}, kwargs)


def img(
    *__content: str | DOMNode,
    alt: str | None = None,
    crossorigin: str | None = None,
    decoding: str | None = None,
    elementtiming: str | None = None,
    fetchpriority: str | None = None,
    height: str | None = None,
    ismap: str | None = None,
    loading: str | None = None,
    referrerpolicy: str | None = None,
    sizes: str | None = None,
    src: str | None = None,
    srcset: str | None = None,
    width: str | None = None,
    usemap: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "img",
        __content,
        {
            "alt": alt,
            "crossorigin": crossorigin,
            "decoding": decoding,
            "elementtiming": elementtiming,
            "fetchpriority": fetchpriority,
            "height": height,
            "ismap": ismap,
            "loading": loading,
            "referrerpolicy": referrerpolicy,
            "sizes": sizes,
            "src": src,
            "srcset": srcset,
            "width": width,
            "usemap": usemap,
        },
        kwargs,
    )


def input(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("input", __content, {}, kwargs)


def ins(
    *__content: str | DOMNode,
    cite: str | None = None,
    datetime: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "ins",
        __content,
        {
            "cite": cite,
            "datetime": datetime,
        },
        kwargs,
    )


def kbd(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("kbd", __content, {}, kwargs)


def label(
    *__content: str | DOMNode,
    html_for: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "label",
        __content,
        {
            "html_for": html_for,
        },
        kwargs,
    )


def legend(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("legend", __content, {}, kwargs)


def li(
    *__content: str | DOMNode,
    value: str | None = None,
    type: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "li",
        __content,
        {
            "value": value,
            "type": type,
        },
        kwargs,
    )


def link(
    *__content: str | DOMNode,
    html_as: str | None = None,
    crossorigin: str | None = None,
    disabled: str | None = None,
    fetchpriority: str | None = None,
    href: str | None = None,
    hreflang: str | None = None,
    imagesizes: str | None = None,
    imagesrcset: str | None = None,
    integrity: str | None = None,
    media: str | None = None,
    prefetch: str | None = None,
    referrerpolicy: str | None = None,
    rel: str | None = None,
    sizes: str | None = None,
    title: str | None = None,
    type: str | None = None,
    blocking: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "link",
        __content,
        {
            "html_as": html_as,
            "crossorigin": crossorigin,
            "disabled": disabled,
            "fetchpriority": fetchpriority,
            "href": href,
            "hreflang": hreflang,
            "imagesizes": imagesizes,
            "imagesrcset": imagesrcset,
            "integrity": integrity,
            "media": media,
            "prefetch": prefetch,
            "referrerpolicy": referrerpolicy,
            "rel": rel,
            "sizes": sizes,
            "title": title,
            "type": type,
            "blocking": blocking,
        },
        kwargs,
    )


def main(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("main", __content, {}, kwargs)


def map(
    *__content: str | DOMNode,
    name: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "map",
        __content,
        {
            "name": name,
        },
        kwargs,
    )


def mark(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("mark", __content, {}, kwargs)


def marquee(
    *__content: str | DOMNode,
    behavior: str | None = None,
    bgcolor: str | None = None,
    direction: str | None = None,
    height: str | None = None,
    hspace: str | None = None,
    loop: str | None = None,
    scrollamount: str | None = None,
    scrolldelay: str | None = None,
    truespeed: str | None = None,
    vspace: str | None = None,
    width: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "marquee",
        __content,
        {
            "behavior": behavior,
            "bgcolor": bgcolor,
            "direction": direction,
            "height": height,
            "hspace": hspace,
            "loop": loop,
            "scrollamount": scrollamount,
            "scrolldelay": scrolldelay,
            "truespeed": truespeed,
            "vspace": vspace,
            "width": width,
        },
        kwargs,
    )


def menu(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("menu", __content, {}, kwargs)


def menuitem(
    *__content: str | DOMNode,
    checked: str | None = None,
    command: str | None = None,
    default: str | None = None,
    disabled: str | None = None,
    icon: str | None = None,
    label: str | None = None,
    radiogroup: str | None = None,
    type: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "menuitem",
        __content,
        {
            "checked": checked,
            "command": command,
            "default": default,
            "disabled": disabled,
            "icon": icon,
            "label": label,
            "radiogroup": radiogroup,
            "type": type,
        },
        kwargs,
    )


def meta(
    *__content: str | DOMNode,
    charset: str | None = None,
    content: str | None = None,
    http_equiv: str | None = None,
    name: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "meta",
        __content,
        {
            "charset": charset,
            "content": content,
            "http_equiv": http_equiv,
            "name": name,
        },
        kwargs,
    )


def meter(
    *__content: str | DOMNode,
    value: str | None = None,
    min: str | None = None,
    max: str | None = None,
    low: str | None = None,
    high: str | None = None,
    optimum: str | None = None,
    form: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "meter",
        __content,
        {
            "value": value,
            "min": min,
            "max": max,
            "low": low,
            "high": high,
            "optimum": optimum,
            "form": form,
        },
        kwargs,
    )


def nav(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("nav", __content, {}, kwargs)


def nobr(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("nobr", __content, {}, kwargs)


def noembed(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("noembed", __content, {}, kwargs)


def noframes(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("noframes", __content, {}, kwargs)


def noscript(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("noscript", __content, {}, kwargs)


def object(
    *__content: str | DOMNode,
    archive: str | None = None,
    border: str | None = None,
    classid: str | None = None,
    codebase: str | None = None,
    codetype: str | None = None,
    data: str | None = None,
    declare: str | None = None,
    form: str | None = None,
    height: str | None = None,
    name: str | None = None,
    standby: str | None = None,
    type: str | None = None,
    usemap: str | None = None,
    width: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "object",
        __content,
        {
            "archive": archive,
            "border": border,
            "classid": classid,
            "codebase": codebase,
            "codetype": codetype,
            "data": data,
            "declare": declare,
            "form": form,
            "height": height,
            "name": name,
            "standby": standby,
            "type": type,
            "usemap": usemap,
            "width": width,
        },
        kwargs,
    )


def ol(
    *__content: str | DOMNode,
    reversed: str | None = None,
    start: str | None = None,
    type: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "ol",
        __content,
        {
            "reversed": reversed,
            "start": start,
            "type": type,
        },
        kwargs,
    )


def optgroup(
    *__content: str | DOMNode,
    disabled: str | None = None,
    label: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "optgroup",
        __content,
        {
            "disabled": disabled,
            "label": label,
        },
        kwargs,
    )


def option(
    *__content: str | DOMNode,
    disabled: str | None = None,
    label: str | None = None,
    selected: str | None = None,
    value: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "option",
        __content,
        {
            "disabled": disabled,
            "label": label,
            "selected": selected,
            "value": value,
        },
        kwargs,
    )


def output(
    *__content: str | DOMNode,
    html_for: str | None = None,
    form: str | None = None,
    name: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "output",
        __content,
        {
            "html_for": html_for,
            "form": form,
            "name": name,
        },
        kwargs,
    )


def p(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("p", __content, {}, kwargs)


def param(
    *__content: str | DOMNode,
    name: str | None = None,
    value: str | None = None,
    type: str | None = None,
    valuetype: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "param",
        __content,
        {
            "name": name,
            "value": value,
            "type": type,
            "valuetype": valuetype,
        },
        kwargs,
    )


def picture(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("picture", __content, {}, kwargs)


def plaintext(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("plaintext", __content, {}, kwargs)


def portal(
    *__content: str | DOMNode,
    referrerpolicy: str | None = None,
    src: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "portal",
        __content,
        {
            "referrerpolicy": referrerpolicy,
            "src": src,
        },
        kwargs,
    )


def pre(
    *__content: str | DOMNode,
    cols: str | None = None,
    width: str | None = None,
    wrap: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "pre",
        __content,
        {
            "cols": cols,
            "width": width,
            "wrap": wrap,
        },
        kwargs,
    )


def progress(
    *__content: str | DOMNode,
    max: str | None = None,
    value: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "progress",
        __content,
        {
            "max": max,
            "value": value,
        },
        kwargs,
    )


def q(
    *__content: str | DOMNode,
    cite: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "q",
        __content,
        {
            "cite": cite,
        },
        kwargs,
    )


def rb(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("rb", __content, {}, kwargs)


def rp(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("rp", __content, {}, kwargs)


def rt(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("rt", __content, {}, kwargs)


def rtc(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("rtc", __content, {}, kwargs)


def ruby(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("ruby", __content, {}, kwargs)


def s(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("s", __content, {}, kwargs)


def samp(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("samp", __content, {}, kwargs)


def script(
    *__content: str | DOMNode,
    html_async: str | None = None,
    crossorigin: str | None = None,
    defer: str | None = None,
    fetchpriority: str | None = None,
    integrity: str | None = None,
    nomodule: str | None = None,
    nonce: str | None = None,
    referrerpolicy: str | None = None,
    src: str | None = None,
    type: str | None = None,
    blocking: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "script",
        __content,
        {
            "html_async": html_async,
            "crossorigin": crossorigin,
            "defer": defer,
            "fetchpriority": fetchpriority,
            "integrity": integrity,
            "nomodule": nomodule,
            "nonce": nonce,
            "referrerpolicy": referrerpolicy,
            "src": src,
            "type": type,
            "blocking": blocking,
        },
        kwargs,
    )


def search(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("search", __content, {}, kwargs)


def section(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("section", __content, {}, kwargs)


def select(
    *__content: str | DOMNode,
    autocomplete: str | None = None,
    autofocus: str | None = None,
    disabled: str | None = None,
    form: str | None = None,
    multiple: str | None = None,
    name: str | None = None,
    required: str | None = None,
    size: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "select",
        __content,
        {
            "autocomplete": autocomplete,
            "autofocus": autofocus,
            "disabled": disabled,
            "form": form,
            "multiple": multiple,
            "name": name,
            "required": required,
            "size": size,
        },
        kwargs,
    )


def slot(
    *__content: str | DOMNode,
    name: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "slot",
        __content,
        {
            "name": name,
        },
        kwargs,
    )


def small(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("small", __content, {}, kwargs)


def source(
    *__content: str | DOMNode,
    type: str | None = None,
    src: str | None = None,
    srcset: str | None = None,
    sizes: str | None = None,
    media: str | None = None,
    height: str | None = None,
    width: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "source",
        __content,
        {
            "type": type,
            "src": src,
            "srcset": srcset,
            "sizes": sizes,
            "media": media,
            "height": height,
            "width": width,
        },
        kwargs,
    )


def span(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("span", __content, {}, kwargs)


def strike(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("strike", __content, {}, kwargs)


def strong(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("strong", __content, {}, kwargs)


def style(
    *__content: str | DOMNode,
    media: str | None = None,
    nonce: str | None = None,
    title: str | None = None,
    blocking: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "style",
        __content,
        {
            "media": media,
            "nonce": nonce,
            "title": title,
            "blocking": blocking,
        },
        kwargs,
    )


def sub(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("sub", __content, {}, kwargs)


def summary(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("summary", __content, {}, kwargs)


def sup(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("sup", __content, {}, kwargs)


def table(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("table", __content, {}, kwargs)


def tbody(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("tbody", __content, {}, kwargs)


def td(
    *__content: str | DOMNode,
    colspan: str | None = None,
    headers: str | None = None,
    rowspan: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "td",
        __content,
        {
            "colspan": colspan,
            "headers": headers,
            "rowspan": rowspan,
        },
        kwargs,
    )


def template(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("template", __content, {}, kwargs)


def textarea(
    *__content: str | DOMNode,
    autocomplete: str | None = None,
    autocorrect: str | None = None,
    autofocus: str | None = None,
    cols: str | None = None,
    dirname: str | None = None,
    disabled: str | None = None,
    form: str | None = None,
    maxlength: str | None = None,
    minlength: str | None = None,
    name: str | None = None,
    placeholder: str | None = None,
    readonly: str | None = None,
    required: str | None = None,
    rows: str | None = None,
    spellcheck: str | None = None,
    wrap: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "textarea",
        __content,
        {
            "autocomplete": autocomplete,
            "autocorrect": autocorrect,
            "autofocus": autofocus,
            "cols": cols,
            "dirname": dirname,
            "disabled": disabled,
            "form": form,
            "maxlength": maxlength,
            "minlength": minlength,
            "name": name,
            "placeholder": placeholder,
            "readonly": readonly,
            "required": required,
            "rows": rows,
            "spellcheck": spellcheck,
            "wrap": wrap,
        },
        kwargs,
    )


def tfoot(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("tfoot", __content, {}, kwargs)


def th(
    *__content: str | DOMNode,
    abbr: str | None = None,
    colspan: str | None = None,
    headers: str | None = None,
    rowspan: str | None = None,
    scope: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "th",
        __content,
        {
            "abbr": abbr,
            "colspan": colspan,
            "headers": headers,
            "rowspan": rowspan,
            "scope": scope,
        },
        kwargs,
    )


def thead(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("thead", __content, {}, kwargs)


def time(
    *__content: str | DOMNode,
    datetime: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "time",
        __content,
        {
            "datetime": datetime,
        },
        kwargs,
    )


def title(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("title", __content, {}, kwargs)


def tr(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("tr", __content, {}, kwargs)


def track(
    *__content: str | DOMNode,
    default: str | None = None,
    kind: str | None = None,
    label: str | None = None,
    src: str | None = None,
    srclang: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "track",
        __content,
        {
            "default": default,
            "kind": kind,
            "label": label,
            "src": src,
            "srclang": srclang,
        },
        kwargs,
    )


def tt(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("tt", __content, {}, kwargs)


def u(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("u", __content, {}, kwargs)


def ul(
    *__content: str | DOMNode,
    compact: str | None = None,
    type: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "ul",
        __content,
        {
            "compact": compact,
            "type": type,
        },
        kwargs,
    )


def var(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("var", __content, {}, kwargs)


def video(
    *__content: str | DOMNode,
    autoplay: str | None = None,
    controls: str | None = None,
    controlslist: str | None = None,
    crossorigin: str | None = None,
    disablepictureinpicture: str | None = None,
    disableremoteplayback: str | None = None,
    height: str | None = None,
    loop: str | None = None,
    muted: str | None = None,
    playsinline: str | None = None,
    poster: str | None = None,
    preload: str | None = None,
    src: str | None = None,
    width: str | None = None,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node(
        "video",
        __content,
        {
            "autoplay": autoplay,
            "controls": controls,
            "controlslist": controlslist,
            "crossorigin": crossorigin,
            "disablepictureinpicture": disablepictureinpicture,
            "disableremoteplayback": disableremoteplayback,
            "height": height,
            "loop": loop,
            "muted": muted,
            "playsinline": playsinline,
            "poster": poster,
            "preload": preload,
            "src": src,
            "width": width,
        },
        kwargs,
    )


def wbr(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("wbr", __content, {}, kwargs)


def xmp(
    *__content: str | DOMNode,
    **kwargs: Unpack[GlobalAttributes],
) -> DOMNode:
    return _node("xmp", __content, {}, kwargs)


def stylesheet(url: str) -> DOMNode:
    return link(rel="stylesheet", href=url)


def js(url: str) -> DOMNode:
    return script(src=url)


__all__ = (
    "a",
    "abbr",
    "acronym",
    "address",
    "area",
    "article",
    "aside",
    "audio",
    "b",
    "base",
    "bdi",
    "bdo",
    "big",
    "blockquote",
    "body",
    "br",
    "button",
    "canvas",
    "caption",
    "center",
    "cite",
    "code",
    "col",
    "colgroup",
    "data",
    "datalist",
    "dd",
    "html_del",
    "details",
    "dfn",
    "dialog",
    "dir",
    "div",
    "dl",
    "dt",
    "em",
    "embed",
    "fieldset",
    "figcaption",
    "figure",
    "font",
    "footer",
    "form",
    "frame",
    "frameset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hgroup",
    "hr",
    "html",
    "i",
    "iframe",
    "image",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "link",
    "main",
    "map",
    "mark",
    "marquee",
    "menu",
    "menuitem",
    "meta",
    "meter",
    "nav",
    "nobr",
    "noembed",
    "noframes",
    "noscript",
    "object",
    "ol",
    "optgroup",
    "option",
    "output",
    "p",
    "param",
    "picture",
    "plaintext",
    "portal",
    "pre",
    "progress",
    "q",
    "rb",
    "rp",
    "rt",
    "rtc",
    "ruby",
    "s",
    "samp",
    "script",
    "search",
    "section",
    "select",
    "slot",
    "small",
    "source",
    "span",
    "strike",
    "strong",
    "style",
    "sub",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "template",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "title",
    "tr",
    "track",
    "tt",
    "u",
    "ul",
    "var",
    "video",
    "wbr",
    "xmp",
    "stylesheet",
    "js",
)
