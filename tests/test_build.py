import os
from pathlib import Path

import pytest

from view import new_app


@pytest.mark.asyncio
async def test_build_requirements():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "build_reqs.toml")

    @app.get("/")
    async def index():
        import pip

        return pip.__file__

    @app.get("/foo", steps=("foo",))
    async def wont_work():
        return "shouldn't be here"

    @app.get("/customreq", steps=("customreq",))
    async def should_work():
        assert os.path.exists("customreq.test")
        return "test"

    @app.get("/failingreq", steps=("failingreq",))
    async def fail():
        return "shouldn't be here"

    async with app.test() as test:
        assert (await test.get("/")).message != ""
        assert (await test.get("/foo")).status == 500
        assert (await test.get("/customreq")).message == "test"
        assert (await test.get("/failingreq")).status == 500
        assert os.path.exists("failingreq.test")


@pytest.mark.asyncio
async def test_build_scripts():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "build_scripts.toml")

    called = False

    @app.get("/", steps=("fail",))
    async def index():
        nonlocal called
        called = True
        return "..."

    async with app.test() as test:
        assert "_VIEW_TEST_BUILD_SCRIPT" in os.environ
        assert (await test.get("/")).status == 500
        assert not called


@pytest.mark.asyncio
async def test_build_commands():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "build_commands.toml")

    @app.get("/", steps=["fail"])
    async def fail():
        return "."

    async with app.test() as test:
        assert (await test.get("/")).status == 500

    assert os.path.exists("build.test")


@pytest.mark.asyncio
async def test_build_platform():
    app = new_app(config_path=Path.cwd() / "tests" / "configs" / "build_platform.toml")

    @app.get("/", steps=["windowsonly"])
    async def index():
        return "hello world"

    async with app.test() as test:
        if os.name == "nt":
            assert (await test.get("/")).message == "hello world"
        else:
            assert (await test.get("/")).status == 500

    assert os.path.exists(
        "linux_build.test" if os.name != "nt" else "windows_build.test"
    )
