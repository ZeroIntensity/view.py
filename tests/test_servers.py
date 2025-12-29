import time

import pytest
import requests

from view.core.app import as_app
from view.core.request import Request
from view.core.response import ResponseLike
from view.run.servers import ServerSettings
from view.status_codes import Success


@pytest.mark.parametrize("server_name", ServerSettings.AVAILABLE_SERVERS)
def test_run_server_detached(server_name: str):
    @as_app
    def app(request: Request) -> ResponseLike:
        header = request.headers["test"]
        assert request.headers["user-agent"].startswith("python-requests")
        return "test", Success.CREATED, {"foo": "bar", "baz": header}

    try:
        __import__(server_name)
    except ImportError:
        pytest.skip(f"{server_name} is not installed")

    process = app.run_detached(server_hint=server_name)
    try:
        time.sleep(1)
        response = requests.get("http://localhost:5000", headers={"test": "silly"})
        assert response.text == "test"
        assert response.status_code == 201
        assert response.headers["foo"] == "bar"
        assert response.headers["baz"] == "silly"
    finally:
        process.kill()
