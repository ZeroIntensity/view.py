import inspect
import logging

from fishhook import hook
from reactpy import component, html, use_state

from src.view import HTML, enable_debug, new_app
from src.view.integrations import page

app = new_app()

enable_debug()
"""
@app.get("/")
@component
def wonderful():
    count, set_count = use_state(0)
    return page(
            html.head(
                html.title("view.py x ReactPy")
            ),
            html.button(
                {"on_click": lambda e: set_count(count + 1)},
                f"you clicked {count} times",
            )
        )
"""

@app.get("/")
async def index():
    return "test", 200, {"a": "b"}

app.run()
