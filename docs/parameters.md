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

!!! danger

    view.py has not yet implemented type checking on parameters

## Body

Bodies work the exact same way, but with the `body` decorator instead:

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
