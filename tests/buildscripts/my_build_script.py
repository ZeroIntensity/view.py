import os

async def __view_build__() -> None:
    os.environ["_VIEW_TEST_BUILD_SCRIPT"] = "1"
    assert __name__ == "__view_build__"