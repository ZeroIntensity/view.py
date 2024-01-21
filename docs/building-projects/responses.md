# Returning Responses

## Basic Responses

In any web framework, returning a response can be as simple as returning a string of text or quite complex with all sorts of things like server-side rendering. Right out of the box, View supports returning status codes, headers, and a response without any fancy tooling. A response **must** contain a body (this is a `str`), but may also contain a status (`int`) or headers (`dict[str, str]`). These may be in any order.

```py
from view import new_app

app = new_app()

@app.get("/")
async def index():
    return "Hello, view.py", 201, {"x-my-header": "my_header"}
```
## Response Protocol

If you have some sort of object that you want to wrap a response around, view.py gives you the `__view_response__` protocol. The only requirements are:

- `__view_response__` is available on the returned object (doesn't matter if it's static or instance)
- `__view_response__` returns data that corresponds to the allowed return values.

For example, a type `MyObject` defining `__view_response__` could look like:

```py
from view import new_app

app = new_app()

class MyObject:
    def __view_response__(self):
        return "Hello from MyObject!", {"x-www-myobject": "foo"}

@app.get("/")
async def index():
    return MyObject()  # this is ok

app.run()
```

Note that in the above scenario, you wouldn't actually need a whole object. Instead, you could also just define a utility function:

```py
def _response():
    return "Hello, view.py!", {"foo": "bar"}

@app.get("/")
async def index():
    return _response()
```

## Response Objects

View comes with two built in response objects: `Response` and `HTML`.

- `Response` is simply a wrapper around other responses.
- `HTML` is for returning HTML content.

::: view.response.Response
::: view.response.HTML

A common use case for `Response` is wrapping an object that has a `__view_response__` and changing one of the values. For example:

```py
from view import new_app, Response

app = new_app()

class Test:
    def __view_result__(self):
        return "test", 201

@app.get("/")
async def index():
    return Response(Test(), status=200)  # 200 is returned, not 201

app.run()
```

Another common case for `Response` is using cookies. You can add a cookie to the response via the `cookie` method:

```py
@app.get("/")
async def index():
    res = Response(...)
    res.cookie("hello", "world")
    return res
```


::: view.response.Response.cookie

Note that **all response classes inherit from `Response`**, meaning you can use this functionality anywhere. 

## Review

Responses can be returned with a string, integer, and/or dictionary in any order.

- The string represents the body of the response (e.g. the HTML or JSON)
- The integer represents the status code (200 by default)
- The dictionary represents the headers (e.g. `{"x-www-my-header": "some value"}`)

`Response` objects can also be returned, which implement the `__view_response__` protocol. All response classes inherit from `Response`, which supports operations like setting cookies.
