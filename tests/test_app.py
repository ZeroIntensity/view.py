from ward import test

from view import new_app
import importlib
import sys

importlib.reload(sys)
sys.setdefaultencoding("UTF8")


@test("app startup")
async def _():
    app = new_app()
    app.load()
