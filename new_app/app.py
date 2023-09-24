from view import new_app, get
from view.databases import PostgresConnection
# import sqlite3


l = {
    "database": "test-db",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": 5432,
}
pg = PostgresConnection(l)

# pg.close()


app = new_app()

# Pretend that both index and about are in seperate files
@get("/")
async def index():
    await pg.connect()
    return "..."

@get("/about")
async def about():
    await pg.close()
    return "..."

app.load((index, about))
app.run()