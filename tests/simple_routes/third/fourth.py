from view import delete, options


@delete("/delete")
async def d():
    return "delete"


@options("/options")
async def o():
    return "options"
