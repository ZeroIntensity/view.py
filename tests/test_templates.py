from pathlib import Path

import pytest

from view import markdown, new_app, render, template


@pytest.mark.asyncio
async def test_view_rendering():
    x = 2

    class Test:
        def __init__(self):
            self.foo = "bar"

    test = Test()
    d = {"hello": "world"}
    assert (await render('<view ref="1" />')) == "1"
    assert (await render('<view ref="x" />')) == "2"
    assert (await render('<view ref="test.foo" />')) == "bar"
    assert (await render("<view ref=\"d['hello']\" />")) == "world"
    assert (await render('<view ref="x" >2</view>')) == "22"

    l = [1, 2, 3]
    assert (await render('<view ref="len(l)" />')) == "3"
    assert (
        await render('<view iter="l" item="i"><view ref="i" /></view>')
    ) == "123"
    assert (await render('<view if="x == 2">hi</view>')) == "hi"
    assert (await render('<view if="x == 1">hi</view>')) == ""
    assert (
        await render(
            '<view if="x == 1">hi</view><view elif="x == 2">2</view><view else>bye</view>'
        )
    ) == "2"
    assert (
        await render(
            '<view if="x == 1">hi</view><view elif="x == 2">2</view><view elif="x == 4">4</view><view else>bye</view>'
        )
    ) == "2"
    assert (
        await render(
            '<view if="x == 1">hi</view><view elif="x == 5">2</view><view elif="x == 4">4</view><view else>bye</view>'
        )
    ) == "bye"


@pytest.mark.asyncio
async def test_other_engines():
    x = "world"
    assert (await render("hello {{ x }}", engine="jinja")) == "hello world"
    assert (await render("hello {{ x }}", engine="django")) == "hello world"
    assert (await render("hello ${x}", engine="mako")) == "hello world"
    assert (await render("hello ${x}", engine="chameleon")) == "hello world"


@pytest.mark.asyncio
async def test_templating():
    app = new_app()

    @app.get("/")
    async def index():
        hi = "hello"
        return await app.template(
            "index.html", directory=Path.cwd() / "tests" / "templates"
        )

    @app.get("/other")
    async def other():
        x = 1
        return await template(
            "something",
            directory=Path.cwd() / "tests" / "other_templates",
            engine="mako",
        )

    @app.get("/markdown")
    async def md():
        return await markdown(
            "test.md", directory=Path.cwd() / "tests" / "templates"
        )

    async with app.test() as test:
        assert (await test.get("/")).message.replace("\n", "") == "hello"
        assert (await test.get("/other")).message.replace("\n", "") == "1"
        assert (await test.get("/markdown")).message.replace(
            "\n", ""
        ) == "<!DOCTYPE html><html><h1>A</h1><h2>B</h2><h3>C</h3></html>"


@pytest.mark.asyncio
async def test_template_configuration_settings():
    app = new_app(
        config_path=Path.cwd() / "tests" / "configs" / "templates.toml"
    )

    @app.get("/")
    async def index():
        x = 1
        return await template("something")

    async with app.test() as test:
        assert (await test.get("/")).message.replace("\n", "") == "1"


@pytest.mark.asyncio
async def test_view_renderer_subtemplates():
    app = new_app(
        config_path=Path.cwd() / "tests" / "configs" / "subtemplates.toml"
    )

    @app.get("/")
    async def index():
        return await template("sub")

    async with app.test() as test:
        assert (await test.get("/")).message.replace("\n", "") == "helloworld"
