from view import new_app, get
from view.databases import PostgresConnection
# import sqlite3


l = {}
pg = PostgresConnection()
pg.connect(l)


app = new_app()

# Pretend that both index and about are in seperate files
@get("/")
async def index():
    return "..."

@get("/about")
async def about():
    return "..."

app.load((index, about))
app.run()