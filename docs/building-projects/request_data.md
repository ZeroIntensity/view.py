# Request Data

## The Context

If you've used a framework like [Django](https://djangoproject.com) or [FastAPI](https://fastapi.tiangolo.com), you've likely used a `request` parameter (or a `Request` type). View has something similiar, called `Context`.

The `Context` instance contains information about the incoming request, including:

- The headers.
- The cookies.
- The HTTP version.
- The request method.
- The URL path.
- The client and server address.

!!! note

    `Context` is an [extension type](https://docs.python.org/3/extending/newtypes_tutorial.html), and is defined in the `_view` module. It's Python signatures are defined in the `_view` type stub.


## Context Input

The context can be added to a route via a route input, which is done through the `context` decorator. Note that `context` has a standard and direct variation (i.e. `App.context` is available to prevent imports).

For example:

```py
from view import new_app, context, Context

app = new_app()

@app.get("/")
@context
async def index(ctx: Context):
    print(ctx.headers["user-agent"])
    return "..."

app.run()
```

Since `context` is a route input, it can be used alongside other route inputs:

```py
from view import new_app, Context

app = new_app()

@app.get("/")
@app.query("greeting", str)
@app.context  # direct variation
async def index(greeting: str, ctx: Context):
    return f"{greeting}, {ctx.headers['place']}"

app.run()
```

### Detecting Tests

`Context` can also be used to detect whether the route is being used via `App.test`
