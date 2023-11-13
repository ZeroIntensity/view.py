# Parameters

## Query Strings and Bodies

If you're familiar with HTTP semantics, then you likely already know about query parameters and body parameters. If you have no idea what that is, that's okay.

In HTTP, the query string is at the end of the URL and is prefixed with a `?`. For example, in a YouTube link (e.g. `youtube.com/watch?v=...`), the query string is `?v=...`. The query string contains key value pairs in the form of strings. In Python, it's similiar to a `dict` that only contains strings.

Bodies are a little bit more complicated. An HTTP body can be a number of different formats, but in a nutshell they are again, key-value pairs, but they can be a number of types. For now, JSON will be the main focus, which can have `str` keys, and any of the following as a value (in terms of Python types):

- `str`
- `int`
- `bool`
- `dict[str, <any of these types>]`

The main similiarity here is that they are both key value pairs, which will make more sense in a moment.

## Route Inputs

In view.py, a route input is anything that feeds a parameter (or "input") to the route. This can be either a parameter received through the HTTP body, or something taken from the query string. View treats these two essentially the same on the user's end. Route inputs are similar to routes in the sense that there are standard and direct versions of the same thing:

- `query` or `App.query`
- `body` or `App.body`

There is little to no difference between the standard and direct variations, **including loading**. The direct versions are only to be used when the app is already available to prevent extra imports.

## Defining Inputs

For documentation purposes, only `query` variations will be used. However, **`body` works the exact same way**. A route input function (`query` in this case) takes one or more parameters:

- The name of the parameter, should be a `str`.
- The type that it expects (optional). Note that this can be passed as many times as you want, and each type is just treated as a union.

The below code would expect a parameter in the query string named `hello` of type `int`:

```py
from view import new_app

app = new_app()

@app.get("/")
@app.query("hello", int)
async def index(hello: int):
    print(hello)
    return "hello"
```
