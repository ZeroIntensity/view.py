import pytest
from view.testing import AppTestClient
from view.app import as_app

@pytest.mark.asyncio
async def test_response():
    assert 1
