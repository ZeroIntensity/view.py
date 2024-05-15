from pathlib import Path

from setuptools._distutils.ccompiler import new_compiler
from setuptools._distutils.sysconfig import customize_compiler
import pytest

from view import new_app


@pytest.mark.asyncio
async def test_build_requirements():
    compiler = new_compiler()
    customize_compiler(compiler)  # type: ignore
    path = compiler.compiler[0]  # type: ignore

    app = new_app(
        config_path=Path.cwd() / "tests" / "configs" / "build_reqs.toml"
    )

    @app.get("/")
    async def index():
        return path

    async with app.test() as test:
        assert (await test.get("/")).message != ""
