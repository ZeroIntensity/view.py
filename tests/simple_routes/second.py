from view import patch, put


@put("/put")
async def pu():
    return "put"


@patch("/patch")
async def pa():
    return "patch"
