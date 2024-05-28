from pathlib import Path

import pytest
from typing import List
from view import delete, get, new_app, options, patch, post, put, App, Route, InvalidCustomLoaderError

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


@pytest.mark.asyncio
async def test_custom_loader():
    app = new_app()
    app.config.app.loader = "custom"

    @app.custom_loader
    def my_loader(app: App, path: Path) -> List[Route]:
        @get("/")
        async def index():
            return "test"

        return [index]

    async with app.test() as test:
        assert (await test.get("/")).message == "test"


def test_custom_loader_errors():
    app = new_app()
    app.config.app.loader = "custom"

    with pytest.raises(InvalidCustomLoaderError):
        app.load()

    @app.custom_loader
    def my_loader(app: App, path: Path) -> List[Route]:
        return 123

    with pytest.raises(InvalidCustomLoaderError):
        app.load()
