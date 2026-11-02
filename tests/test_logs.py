import asyncio
from contextlib import asynccontextmanager
from io import StringIO
from unittest.mock import patch

import pytest
from rich.console import Console
from rich.text import Text

from view.__about__ import __version__
from view.core.app import App
from view.logs import Logger, LogLevels, LogManager
from view.testing import AppTestClient


@pytest.fixture
def logs():
    output = StringIO()
    manager = LogManager(console=Console(file=output, width=200))
    return manager, output


@pytest.mark.parametrize(
    "level", ["debug", "info", "warning", "error", "critical"]
)
def test_immediate_logging(logs, level):
    manager, output = logs
    manager.level = LogLevels.DEBUG
    logger = manager.create_logger("test")

    getattr(logger, level)("message", Text("renderable"))

    assert "[test]" in output.getvalue()
    assert level in output.getvalue()
    assert "message renderable" in output.getvalue()
    assert not manager.running


def test_level_filtering_and_disabling(logs):
    manager, output = logs
    logger = manager.create_logger("test")
    logger.debug("filtered debug")
    logger.info("visible info")
    logger.level = LogLevels.ERROR
    logger.warning("filtered warning")
    logger.error("visible error")
    manager.level = LogLevels.CRITICAL
    logger.error("filtered error")
    logger.critical("visible critical")
    logger.disabled = True
    logger.critical("disabled critical")
    logger.exception("disabled exception")

    assert "filtered" not in output.getvalue()
    assert "disabled" not in output.getvalue()
    assert "visible info" in output.getvalue()
    assert "visible error" in output.getvalue()
    assert "visible critical" in output.getvalue()


@pytest.mark.asyncio
async def test_queued_logs_drain_and_manager_can_restart(logs):
    manager, output = logs
    logger = manager.create_logger("test")

    for _ in range(2):
        output.seek(0)
        output.truncate()
        async with manager:
            assert manager.running
            assert LogManager.current() is manager
            logger.info("first message")
            logger.info("last message")
            assert output.getvalue() == ""

        assert not manager.running
        assert output.getvalue().index(
            "first message"
        ) < output.getvalue().index("last message")
        with pytest.raises(RuntimeError, match="no log manager"):
            LogManager.current()


@pytest.mark.asyncio
async def test_nested_managers_restore_context_on_error(logs):
    manager, output = logs
    async with manager:
        with pytest.raises(ValueError, match="test failure"):
            async with LogManager() as nested:
                assert LogManager.current() is nested
                manager.create_logger("test").info("drained on error")
                raise ValueError("test failure")
        assert LogManager.current() is manager
    assert "drained on error" in output.getvalue()


@pytest.mark.asyncio
async def test_queued_exception_captures_original_traceback(logs):
    manager, output = logs
    async with manager:
        try:
            raise ValueError("original failure")
        except ValueError:
            manager.create_logger("test").exception("request failed")

    assert "request failed" in output.getvalue()
    assert "ValueError: original failure" in output.getvalue()
    assert output.getvalue().count("[test]") == 1


@pytest.mark.asyncio
async def test_log_time_reports_milliseconds_and_warns(logs):
    manager, output = logs
    manager.level = LogLevels.DEBUG
    logger = manager.create_logger("test")

    with patch("view.logs.time.perf_counter", side_effect=[1.0, 1.25]):
        async with logger.log_time("operation", warning_time=0):
            await asyncio.sleep(0.01)

    assert "operation is slow" in output.getvalue()
    assert "operation took 250.0ms" in output.getvalue()


@pytest.mark.asyncio
async def test_wrap_log_time_handles_context_entry_failure(logs):
    manager, output = logs
    manager.level = LogLevels.DEBUG
    logger = manager.create_logger("test")
    tasks_before = asyncio.all_tasks()

    @asynccontextmanager
    async def failing_context():
        raise ValueError("startup failed")
        yield

    with pytest.raises(ValueError, match="startup failed"):
        async with logger.wrap_log_time("startup", failing_context()):
            pytest.fail("context entry should fail")

    assert "startup took" in output.getvalue()
    assert asyncio.all_tasks() == tasks_before


@pytest.mark.asyncio
async def test_wrap_log_time_only_measures_context_entry(logs):
    manager, output = logs
    manager.level = LogLevels.DEBUG
    logger = manager.create_logger("test")
    exited = False

    @asynccontextmanager
    async def context():
        nonlocal exited
        try:
            yield "ready"
        finally:
            exited = True

    async with logger.wrap_log_time("startup", context()) as result:
        assert result == "ready"
        assert "startup took" in output.getvalue()
        assert not exited
    assert exited


@pytest.mark.asyncio
@pytest.mark.parametrize("development_mode", ["0", "1"])
async def test_app_logging_and_shut_up(monkeypatch, logs, development_mode):
    monkeypatch.setenv("VIEW_DEVMODE", development_mode)
    manager, output = logs
    app = App()
    assert isinstance(app.logger, Logger)
    assert app.logger.level == (
        LogLevels.DEBUG if development_mode == "1" else LogLevels.INFO
    )
    app.logger.manager.console = manager.console

    @app.get("/")
    def index():
        return "ok"

    client = AppTestClient(app)
    assert await (await client.get("/")).body() == b"ok"
    assert "GET on route /" in output.getvalue()
    assert "%s" not in output.getvalue()

    output.seek(0)
    output.truncate()
    app.shut_up()
    assert await (await client.get("/")).body() == b"ok"
    assert output.getvalue() == ""


def test_startup_banner_uses_view_version(logs):
    manager, output = logs
    manager.print_startup_message()
    assert r"|___/_/\___/|__/|__(_) .___/\__, /" in output.getvalue()
    assert f"v{__version__}" in output.getvalue()
