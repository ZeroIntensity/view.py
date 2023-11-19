from view import get


@get()
async def g():
    return "get"
