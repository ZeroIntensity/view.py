from view import get, post


@get("/get")
async def g():
    return "get"


@post("/post")
async def p():
    return "post"
