import asyncio
import secrets
from contextlib import suppress
from functools import partial
from pathlib import Path

import exceptiongroup
from reactpy import component, html, use_state, vdom_to_html
from reactpy.backend.hooks import ConnectionContext
from reactpy.backend.types import Connection, Location
from reactpy.core.layout import Layout
from reactpy.core.serve import serve_layout
from reactpy.core.types import VdomDict, VdomJson
from reactpy.core.vdom import make_vdom_constructor

from src.view import (HTML, Context, Router, WebSocket,
                      WebSocketDisconnectError, new_app)

_html = make_vdom_constructor("html")
_body = make_vdom_constructor("body")


def page(head: VdomDict, *body: VdomDict, lang: str = "en") -> VdomDict:
    return _html({"lang": lang}, head, _body(*body))


@component
def ReactPyView():
    count, set_count = use_state(0)
    return page(
        html.head(html.title("view.py x React")),
        html.button(
            {"on_click": lambda e: set_count(count + 1)},
            f"you clicked {count} times",
        ),
    )


app = new_app()


@app.get("/")
@app.context
async def index(ctx: Context):
    hook = secrets.token_hex(64)
    component = ReactPyView()
    app._reactive_sessions[hook] = component

    async with Layout(
        ConnectionContext(
            component,
            value=Connection(
                {"reactpy": {"id": hook}},
                Location(ctx.path, ""),
                carrier=None,
            ),
        )
    ) as layout:
        # this is especially ugly, but reactpy renders
        # the first few nodes as nothing
        # for whatever reason.
        vdom: VdomJson = (await layout.render())["model"]["children"][0][
            "children"
        ][0]["children"][0]

    if vdom["tagName"] != "html":
        raise RuntimeError(
            "root react component must be html (see view.page())"
        )

    children = vdom.get("children")
    if not children:
        raise RuntimeError("root react component has no children")

    head: VdomDict = children[0]
    if head["tagName"] != "head":
        raise RuntimeError(
            f"expected a <head> element, got <{head['tagName']}>"
        )

    body: VdomDict = children[1]
    if body["tagName"] != "body":
        raise RuntimeError(
            f"expected a <body> element, got <{body['tagName']}>"
        )

    prerender_head = vdom_to_html(head)
    prerender_body = vdom_to_html(body)
    return await app.template(
        "./client/dist/index.html",
        directory=Path("./"),
        engine="view",
    )


@app.websocket("/_view/reactpy-stream")
@app.query("route", str)
async def index_ws(ws: WebSocket, route: str):
    try:
        page = app._reactive_sessions[route.strip("\n")]
    except KeyError:
        return "Invalid route stream ID"

    await ws.accept()
    with suppress(exceptiongroup.ExceptionGroup):
        await serve_layout(
            Layout(ConnectionContext(page)),  # type: ignore
            ws.send,  # type: ignore
            partial(ws.receive, tp=dict),  # type: ignore
        )


app.run()
