from ward import test

from view import new_app
import importlib
import sys

@test("app startup")
async def _():
    app = new_app()
    app.load()
