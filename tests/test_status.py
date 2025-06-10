import pytest
from conftest import limit_leaks

from view import ERROR_CODES, HTTPError, InvalidStatusError, new_app

STATUS_CODES = (
    200,
    201,
    202,
    203,
    204,
    205,
    206,
    207,
    208,
    226,
    300,
    301,
    302,
    303,
    304,
    305,
    307,
    308,
)


@pytest.mark.asyncio
@limit_leaks("1 MB")
async def test_returning_the_proper_status_code():
    app = new_app()

    @app.get("/")
    async def index(status: int):
        return "hello", status

    @app.get("/error")
    async def err(status: int):
        raise HTTPError(status)  # type: ignore

    @app.get("/fail")
    async def fail():
        with pytest.raises(InvalidStatusError):
            raise HTTPError(200)  # type: ignore

        with pytest.raises(InvalidStatusError):
            raise HTTPError(600)  # type: ignore

        return ""

    async with app.test() as test:
        for status in [*STATUS_CODES, *ERROR_CODES]:
            assert (await test.get("/", query={"status": status})).status == status

        for status in ERROR_CODES:
            assert (await test.get("/error", query={"status": status})).status == status
