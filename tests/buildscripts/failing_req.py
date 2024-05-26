import aiofiles

async def __view_requirement__() -> bool:
    async with aiofiles.open("failingreq.test", "w"):
        pass
    
    return False