from pathlib import Path

from ward import test

from view import delete, get, new_app, options, patch, post, put


@test("manual loader")
async def _():
    app = new_app()
    assert app.config.app.loader == "manual"

    @get("/get")
    async def g():
        return "get"

    @post("/post")
    async def p():
        return "post"

    @put("/put")
    async def pu():
        return "put"

    @patch("/patch")
    async def pa():
        return "patch"

    @delete("/delete")
    async def d():
        return "delete"

    @options("/options")
    async def o():
        return "options"

    app.load([g, p, pu, pa, d, o])

    async with app.test() as test:
        assert (await test.get("/get")).message == "get"
        assert (await test.post("/post")).message == "post"
        assert (await test.put("/put")).message == "put"
        assert (await test.patch("/patch")).message == "patch"
        assert (await test.delete("/delete")).message == "delete"
        assert (await test.options("/options")).message == "options"


@test("simple loader")
async def _():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "simple.toml")

    async with app.test() as test:
        assert (await test.get("/get")).message == "get"
        assert (await test.post("/post")).message == "post"
        assert (await test.put("/put")).message == "put"
        assert (await test.patch("/patch")).message == "patch"
        assert (await test.delete("/delete")).message == "delete"
        assert (await test.options("/options")).message == "options"


@test("filesystem loader")
async def _():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "fs.toml")

    async with app.test() as test:
        assert (await test.get("/get")).message == "get"
        assert (await test.post("/post")).message == "post"
        assert (await test.put("/put")).message == "put"
        assert (await test.patch("/patch")).message == "patch"
        assert (await test.delete("/delete")).message == "delete"
        assert (await test.options("/options")).message == "options"


@test("patterns loader")
async def _():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "urls.toml")

    async with app.test() as test:
        assert (await test.get("/get")).message == "get"
        assert (await test.post("/post")).message == "post"
        assert (await test.put("/put")).message == "put"
        assert (await test.patch("/patch")).message == "patch"
        assert (await test.delete("/delete")).message == "delete"
        assert (await test.options("/options")).message == "options"
