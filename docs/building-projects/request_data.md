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

The context can be added to a route via a route input, which is done through the `context` decorator. Note that `context` has a standard and direct variation (`App.context` is available to prevent imports).

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

### Automatic Input

`Context` works well with the automatic input API (similar to how you would do it in [FastAPI](https://fastapi.tiangolo.com)), like so:

```py
from view import new_app, Context

app = new_app()

@app.get("/")
async def index(ctx: Context):  # this is allowed
    ...

app.run()
```

## Detecting Tests

`Context` can also be used to detect whether the route is being used via `App.test`, through the `http_version` attribute.

!!! note

    `App.test` is a more internal detail, but is available to use publically. It looks like this:

    ```py
    from view import new_app
    import asyncio

    app = new_app()

    @app.get("/")
    async def index():
        return "hello, view.py"

    async def main():
        async with app.test() as test:
            res = await test.get("/")
            assert res.message == "hello, view.py"

    if __name__ == "__main__":
        asyncio.run(main())
    ```

When a route is being used via `App.test`, `http_version` is set to `view_test`. For example:

```py
from view import new_app, Context
import asyncio

app = new_app()

@app.get("/")
@app.context
async def index(context: Context):
    if context.http_version == "view_test":
        return "this is a test!"

    return "hello, view.py"

async def main():
    async with app.test() as test:
        res = await test.get("/")
        assert res.message == "this is a test!"

if __name__ == "__main__":
    asyncio.run(main())
```

## Cookies

Technically speaking, cookies in HTTP are done via [headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cookie), but typically cookies in Python frameworks are done in a `dict` instead. View is no exception to this.

Cookies can be viewed from the `cookies` attribute. However, since the `Context` is **not related** to the response, you must use `cookie` on a `Response` object to mutate a cookie. For example:

```py
from view import new_app, Context, Response

app = new_app()

@app.get("/")
async def index(ctx: Context):  # automatic route input
    count = int(ctx.cookies.get("count") or 0)
    count += 1
    res = Response(f"you have been to this page {count} time(s)")
    res.set_cookie("count", str(count))
    return res

app.run()
```

## Server and Client Address

## Review

`Context` is similiar to `Request` in other web frameworks, and is considered to be a route input in View. `Context` contains eight attributes:

- `headers`, of type `dict[str, str]`.
- `cookies`, of type `dict[str, str]`.
- `client`, of type `ipaddress.IPv4Address`, `ipaddress.IPv6Address`, or `None`.
- `server`, of type `ipaddress.IPv4Address`, `ipaddress.IPv6Address`, or `None`.
- `method`, of type `StrMethodASGI` (uppercase string containing the method, such as `"GET"`).
- `path`, of type `str`.
- `scheme`, which can be the string `"http"`, `"https"`.
- `http_version`, which can be the string `"1.0"`, `"1.1"`, `"2.0"`, `"view_test"`.
