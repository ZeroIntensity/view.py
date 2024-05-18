import os
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from view import new_app


@pytest.mark.asyncio
async def test_build_requirements():
    app = new_app(
        config_path=Path.cwd() / "tests" / "configs" / "build_reqs.toml"
    )

    @app.get("/")
    async def index():
        import pip

        return pip.__file__

    @app.get("/foo", steps=("foo",))
    async def wont_work():
        return "shouldn't be here"

    async with app.test() as test:
        assert (await test.get("/")).message != ""
        assert (await test.get("/foo")).status == 500


@pytest.mark.asyncio
async def test_build_scripts():
    app = new_app(
        config_path=Path.cwd() / "tests" / "configs" / "build_scripts.toml"
    )

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
    app = new_app(
        config_path=Path.cwd() / "tests" / "configs" / "build_commands.toml"
    )

    @app.get("/", steps=["fail"])
    async def fail():
        return "."

    buffer = StringIO()
    with redirect_stdout(buffer):
        async with app.test() as test:
            assert (await test.get("/")).status == 500
