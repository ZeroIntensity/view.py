from pathlib import Path

import pytest

from view import delete, get, new_app, options, patch, post, put


@pytest.mark.asyncio
async def test_manual_loader():
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


@pytest.mark.asyncio
async def test_simple_loader():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "simple.toml")

    async with app.test() as test:
        assert (await test.get("/get")).message == "get"
        assert (await test.post("/post")).message == "post"
        assert (await test.put("/put")).message == "put"
        assert (await test.patch("/patch")).message == "patch"
        assert (await test.delete("/delete")).message == "delete"
        assert (await test.options("/options")).message == "options"


@pytest.mark.asyncio
async def test_filesystem_loader():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "fs.toml")

    async with app.test() as test:
        assert (await test.get("/get")).message == "get"
        assert (await test.post("/post")).message == "post"
        assert (await test.put("/put")).message == "put"
        assert (await test.patch("/patch")).message == "patch"
        assert (await test.delete("/delete")).message == "delete"
        assert (await test.options("/options")).message == "options"


@pytest.mark.asyncio
async def test_patterns_loader():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "urls.toml")

    async with app.test() as test:
        assert (await test.get("/get")).message == "get"
        assert (await test.post("/post")).message == "post"
        assert (await test.put("/put")).message == "put"
        assert (await test.patch("/patch")).message == "patch"
        assert (await test.delete("/delete")).message == "delete"
        assert (await test.options("/options")).message == "options"
        assert (await test.options("/any")).message == "any"
        assert (await test.post("/inputs", query={"a": "a"})).message == "a"
