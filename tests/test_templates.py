from view import new_app, template, render
from ward import test
from pathlib import Path

@test("view rendering")
async def _():
    x = 2
    
    class Test:
        def __init__(self):
            self.foo = "bar"

    test = Test()
    d = {"hello": "world"}
    assert (await render('<view ref="1" />')) == "1"
    assert (await render('<view ref="x" />')) == "2"
    assert (await render('<view ref="test.foo" />')) == "bar"
    assert (await render('<view ref="d[\'hello\']" />')) == "world"
    assert (await render('<view ref="x" >2</view>')) == "22"

    l = [1, 2, 3]
    assert (await render('<view ref="len(l)" />')) == "3"
    assert (await render('<view iter="l" item="i"><view ref="i" /></view>')) == "123"
    assert (await render('<view if="x == 2">hi</view>')) == "hi"
    assert (await render('<view if="x == 1">hi</view>')) == ""
    assert (await render('<view if="x == 1">hi</view><view elif="x == 2">2</view><view else>bye</view>')) == "2"
    assert (await render('<view if="x == 1">hi</view><view elif="x == 2">2</view><view elif="x == 4">4</view><view else>bye</view>')) == "2"
    assert (await render('<view if="x == 1">hi</view><view elif="x == 5">2</view><view elif="x == 4">4</view><view else>bye</view>')) == "bye"


@test("other engines")
async def _():
    x = "world"
    assert (await render("hello {{ x }}", engine="jinja")) == "hello world"
    assert (await render("hello {{ x }}", engine="django")) == "hello world"
    assert (await render("hello ${x}", engine="mako")) == "hello world"
    assert (await render("hello ${x}", engine="chameleon")) == "hello world"

@test("templating")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        hi = "hello"
        return await template("index.html", directory=Path.cwd() / "tests" / "templates")
    
    @app.get("/other")
    async def other():
        x = 1
        return await template(
            "something",
            directory=Path.cwd() / "tests" / 'other_templates',
            engine="mako",
        )

    async with app.test() as test:
        assert (await test.get("/")).message.replace("\n", "") == "hello"
        assert (await test.get("/other")).message.replace("\n", "") == "1"

@test("template configuration settings")
async def _():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "templates.toml")

    @app.get("/")
    async def index():
        x = 1
        return await template("something")
    
    async with app.test() as test:
        assert (await test.get("/")).message.replace("\n", "") == "1"

@test("view renderer subtemplates")
async def _():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "subtemplates.toml")

    @app.get("/")
    async def index():
        return await template("sub")
    
    async with app.test() as test:
        assert (await test.get("/")).message.replace("\n", "") == "helloworld"
