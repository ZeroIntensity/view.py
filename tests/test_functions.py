from ward import test

from view import App, get_app, new_app


@test("app creation")
def _():
    app = new_app()
    assert isinstance(app, App)
    app.load()


@test("app fetching")
def _():
    app = new_app()
    assert isinstance(get_app(), App)
    app.load()
    assert app is get_app()
