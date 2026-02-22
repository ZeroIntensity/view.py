import subprocess
import sys
import time
import platform

import pytest
import requests
from view.core.app import as_app
from view.core.request import Request
from view.core.response import ResponseLike
from view.core.status_codes import Success
from view.run.servers import ALL_SERVERS

from threading import Lock

_PORT_LOCK = Lock()
_PORT: int = 5000

@pytest.fixture(scope="function")
def port() -> int:
    with _PORT_LOCK:
        global _PORT
        _PORT += 1
        return _PORT


def wait_for_server(port: int, timeout: float = 10.0, interval: float = 0.1) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            requests.get(f"http://localhost:{port}", timeout=1)
            return True
        except requests.ConnectionError:
            time.sleep(interval)
    return False


@pytest.mark.parametrize("server_name", ALL_SERVERS)
@pytest.mark.skipif(platform.system() != "Linux", reason="this has issues on non-Linux")
def test_run_server(server_name: str, port: int):
    try:
        __import__(server_name)
    except ImportError:
        pytest.skip(f"{server_name} is not installed")

    code = f"""if True:
    from view.core.app import App

    app = App()

    @app.get('/')
    async def index():
        return 'ok'

    app.run(server_hint={server_name!r}, port={port})
    """
    process = subprocess.Popen([sys.executable, "-c", code])
    try:
        if not wait_for_server(port):
            pytest.fail("Server did not start in time")
        response = requests.get(f"http://localhost:{port}")
        assert response.text == "ok"
    finally:
        process.kill()


@pytest.mark.parametrize("server_name", ALL_SERVERS)
@pytest.mark.skip("some multiprocessing problems at the moment")
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
        time.sleep(2)
        response = requests.get("http://localhost:5000", headers={"test": "silly"})
        assert response.text == "test"
        assert response.status_code == 201
        assert response.headers["foo"] == "bar"
        assert response.headers["baz"] == "silly"
    finally:
        process.kill()
