# User Guide

This is view.py's documentation for new users. For questions, comments, or concerns you can ask in [our discord](https://discord.gg/tZAfuWAbm2) or [make an issue](https://github.com/ZeroIntensity/view.py/issues).


!!! note "Confused about anything?"
    
    view.py is always looking for changes to documentation. If you have any suggestions, be sure to make an issue.


## Quickstart

If you're not looking for an in depth explanation of anything and can figure out how to use it from API examples, here are some examples:

### Manual Routing

```py
from view import new_app

app = new_app()

@app.get("/")
async def index():
    return "Hello, view.py!"

app.run()
```
### Responses

```py
from view import new_app, Response

app = new_app()

@app.get("/")
def index():
    return "hello", 201


@app.get("/object")
def response_object():
    return Response("hello", 201)
```

### Components

```py
from view import new_app, h1, div

app = new_app()

@app.get("/")
def components():
    return div(h1("Hello, view.py"), cls="flex items-center justify-center")
```

### Queries and Bodies

```py
from view import new_app
from dataclasses import dataclass

app = new_app()


@dataclass
class Name:
    first: str
    last: str


@app.query("hello", str)
@app.query("name", Name, None)
async def index(hello: str, name: Name | None):
    real_name = (name.first + name.last) if name else "view.py"
    return f"{hello}, {real_name}"
```


