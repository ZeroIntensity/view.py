from view import new_app, get
from view.databases import SQLiteConnection, PostgresConnection, MySQLConnection, MongoDBConnection
# import sqlite3



# pg = PostgresConnection("test-db", "postgres","123456", "localhost", 5432)
# sqlite = SQLiteConnection("test-db")

mysql = MySQLConnection("locahost", "debian-sys-maint", "F4m0EQQTyvxiMDoy", "mysql_db")
mongodb = MongoDBConnection("aryaman", 2707, "aryaman-1696252138240", "", "tes-db")
# pg.close()


app = new_app()

# Pretend that both index and about are in seperate files
@get("/")
async def index():
    await mongodb.connect()
    return "connected"

@get("/about")
async def about():
    await mongodb.close()
    return "conn closed"

app.load((index, about))
app.run()