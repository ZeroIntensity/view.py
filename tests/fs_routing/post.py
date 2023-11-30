from view import post


@post()
async def p():
    return "post"
