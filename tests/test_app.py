from ward import test

from view import new_app


@test("app startup")
async def _():
    app = new_app()
    app.config.log.fancy = False
    proc = app.run_task()
    proc.cancel()
