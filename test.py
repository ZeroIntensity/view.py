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

@app.get("/")
@app.context
async def index(ctx: Context):
    print(ctx.headers.get("user-agent"))
    return "abc", 201

app.run()
