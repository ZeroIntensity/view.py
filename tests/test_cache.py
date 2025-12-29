import time
from unittest.mock import patch

import pytest

from view.app import App
from view.cache import InMemoryCache, in_memory_cache, minutes
from view.response import ResponseLike
from view.testing import AppTestClient


@pytest.mark.asyncio
async def test_in_memory_cache():
    app = App()
    called = 0

    @app.get("/")
    @in_memory_cache()
    async def index() -> ResponseLike:
        nonlocal called
        called += 1
        return "test"

    client = AppTestClient(app)
    await client.get("/")
    assert called == 1
    for _ in range(3):
        await client.get("/")
        assert called == 1

    assert isinstance(index.view, InMemoryCache)
    index.view.invalidate()
    await client.get("/")
    assert called == 2


@pytest.mark.asyncio
async def test_in_memory_cache_timeout():
    app = App()

    called = 0

    @app.get("/")
    @in_memory_cache(minutes(2))
    async def index() -> ResponseLike:
        nonlocal called
        called += 1
        return "test"

    client = AppTestClient(app)
    await client.get("/")
    assert called == 1

    for _ in range(100):
        await client.get("/")

    assert called == 1
    now = time.time()
    with patch("time.time", return_value=now + minutes(2)):
        await client.get("/")
        assert called == 2
