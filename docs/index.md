<div align="center"><img src="https://raw.githubusercontent.com/ZeroIntensity/view.py/master/html/logo.png" alt="view.py logo" width=300 height=auto /></div>

## A new web framework.

```py
from view import new_app, h1

@app.get("/")
def index():
    return h1("Hello, view.py!")

app.run()
```
