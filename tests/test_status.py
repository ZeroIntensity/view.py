import pytest

from view import ERROR_CODES, Error, InvalidStatusError, new_app

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
async def test_returning_the_proper_status_code():
    app = new_app()

    @app.get("/")
    async def index(status: int):
        return "hello", status

    @app.get("/error")
    async def err(status: int):
        raise Error(status)

    @app.get("/fail")
    async def fail():
        with pytest.raises(InvalidStatusError):
            raise Error(200)

        with pytest.raises(InvalidStatusError):
            raise Error(600)

        return ""

    async with app.test() as test:
        for status in [*STATUS_CODES, *ERROR_CODES]:
            assert (await test.get("/", query={"status": status})).status == status

        for status in ERROR_CODES:
            assert (await test.get("/error", query={"status": status})).status == status
