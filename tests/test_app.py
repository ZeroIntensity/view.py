from ward import test

from view import new_app


@test("app startup")
def _():
    app = new_app()
    app.load()
    proc = app.run_proc()
    proc.kill()
