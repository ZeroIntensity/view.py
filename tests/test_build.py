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
        return ""

    async with app.test() as test:
        assert (await test.get("/")).message != ""
