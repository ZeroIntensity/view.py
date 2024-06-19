import inspect
import logging

from fishhook import hook

from src.view import new_app

app = new_app()

@app.get("/")
async def index():
    return "test"

app.run()
