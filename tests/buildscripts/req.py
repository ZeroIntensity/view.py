import aiofiles

async def __view_requirement__() -> bool:
    async with aiofiles.open("customreq.test", "w"):
        pass
    return True