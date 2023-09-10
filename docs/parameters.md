# Parameters

## Query Strings

You can add a query string parameter to your route via the `query` decorator:

```py
from view import new_app, query

app = new_app()

@app.get("/hello")
@query("name", str)
async def hello(name: str):
    return p(f"Hello, {name}")

app.run()
```

The first argument is the name of the parameter in the query string, **not the argument name**, and the second argument is the type that it should take.

## Body

Bodies work the exact same way as queries, but with the `body` decorator instead:

```py
@app.get("/goodbye")
@body("name", str)
async def goodbye(name: str):
    return p(f"Bye, {name}")
```

!!! warning

    As of now, only bodies sent in JSON are supported.

## Path

Path parameters are even simpler, just wrap a route part in brackets, like so:

```
@app.get("/hello/{name}")
async def hello(name: str):
    return p(f"Your name is: {name}")
```

Now in the browser, if you were to go to `/hello/world`, the `name` parameter above would be `world`.

Here's a more complicated example:

```py
@app.get("/auth/{user_id}/something/{token}")
async def token(user_id: str, token: str):
    # ...
    return p("Successfully authorized!")
```

!!! danger

    This is extremely buggy and not yet recommended for general use.

## Type Validation

view.py will ensure that the type sent to the server is compatible with what you passed to the decorator. For example:

```py
@app.get("/")
@query("number", int)
async def index(number: int):
    # number will always be an int.
    # if it isn't, an error 400 is sent back to the user automatically
    return "..."
```

The following types are supported:

- `typing.Any`
- `str`
- `int`
- `bool`
- `float`
- `dict` (or `typing.Dict`)
- `None`

You can allow unions by just passing more parameters:

```py
@app.get('/hello')
@query("name", str, None)
async def hello(name: str | None):
    if not name:
        return "hello world"

    return f"hello {name}"
```

You can pass type arguments to a `dict`, which are also validated by the server:

```py
@app.get("/something")
@body("data", dict[str, int])  # typing.Dict on 3.8 and 3.9
async def something(data: dict[str, int]):
    # data will always be a dictionary of strings and integers
    return "..."
```

The key in a dictionary must always be `str` (i.e. `dict[int, str]` is not allowed), but the value can be any supported type (including other dictionaries!)

