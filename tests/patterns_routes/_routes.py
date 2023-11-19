from view import delete, get, options, patch, post, put


@get("/bad")
async def g():
    return "get"


@post()
async def p():
    return "post"


async def pu():
    return "put"


@patch()
async def pa():
    return "patch"


@delete()
async def d():
    return "delete"


@options()
async def o():
    return "options"
