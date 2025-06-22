from view.app import new_app
from view.responses import HTML

app = new_app()

@app.get("/")
def index():
    return HTML.from_file("index/test.html")

if __name__ == "__main__":
    app.run()
