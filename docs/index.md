# Welcome to view.py's documentation!

## A new web framework.

```py
from view import new_app, h1

@app.get("/")
def index():
    return h1("Hello, view.py!")

app.run()
```
