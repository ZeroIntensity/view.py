from ward import test

from view import new_app


@test("app startup")
async def _():
    app = new_app()
    app.load()
