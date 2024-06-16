import asyncio
import secrets
from contextlib import suppress
from functools import partial
from pathlib import Path

import exceptiongroup
from reactpy import component, html, use_state, vdom_to_html
from reactpy.backend.types import Connection, Location
from reactpy.core.layout import Layout
from reactpy.core.serve import serve_layout
from reactpy.core.types import VdomDict, VdomJson
from reactpy.core.vdom import make_vdom_constructor

from src.view import (HTML, Context, Router, WebSocket,
                      WebSocketDisconnectError, new_app)

app = new_app()

@app.get("/")
@component
def test():
    count, set_count = use_state(0)
    return page(
        html.head(html.title("view.py x React")),
        html.button(
            {"on_click": lambda e: set_count(count + 1)},
            f"you clicked {count} times",
        ),
    )


app.run()
