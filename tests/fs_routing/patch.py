from view import patch


@patch()
async def p():
    return "patch"
