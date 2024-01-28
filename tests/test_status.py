from ward import test

from view import Error, new_app

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
ERROR_CODES = (
    400,
    401,
    402,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    421,
    422,
    423,
    424,
    425,
    426,
    428,
    429,
    431,
    451,
    500,
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    510,
    511,
)


@test("returning the proper status code")
async def _():
    app = new_app()

    @app.get("/")
    async def index(status: int):
        return "hello", status

    @app.get("/error")
    async def err(status: int):
        raise Error(status)

    async with app.test() as test:
        for status in [*STATUS_CODES, *ERROR_CODES]:
            assert (
                await test.get("/", query={"status": status})
            ).status == status

        for status in ERROR_CODES:
            assert (
                await test.get("/error", query={"status": status})
            ).status == status
