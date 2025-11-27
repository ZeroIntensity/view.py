from view.app import new_app
from view.status_codes import Success
from view.dom import html_response, h1, html, head, body, title

app = new_app()

@app.get("/")
@html_response
def index():
    yield Success.OK

    with html():
        with head():
            yield title("Hello, view.py!")

        with body():
            yield h1("My first page")


if __name__ == "__main__":
    app.run(production=True)
