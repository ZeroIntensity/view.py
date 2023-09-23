from view.routing import get

@get('/')
async def index():
    return 'Hello, view.py!'
