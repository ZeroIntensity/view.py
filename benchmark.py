import os
import time
import timeit
from contextlib import redirect_stderr, redirect_stdout
from threading import Thread

import uvicorn
from fastapi import FastAPI

from view import new_app

fastapi = FastAPI()
view = new_app()


@fastapi.get("/")
def froute():
    return "hello, world"


@view.get("/")
async def vroute():
    return "hello, world"


Thread(
    target=uvicorn.run, args=(fastapi,), kwargs={"port": 8000}, daemon=True
).start()
view.run_threaded()

time.sleep(3)
