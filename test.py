from reactpy import component, html, use_state

from src.view import Context, new_app, page

app = new_app()
"""
@app.get("/")  # type: ignore
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
"""

class Test:
    def __view_result__(self):
        return "broken!"

@app.get("/")
@app.context
async def index(ctx: Context):
    return Test()

app.run()
