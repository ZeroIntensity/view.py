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

## HTTP Errors

Generally when returning a [client error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses) or [server error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#server_error_responses), you want to skip future execution. For example:

```py
from view import new_app

app = new_app()

@app.get("/")
async def index(number: int):
    if number == 1:
        return "number cannot be one", 400

    return f"your number is {number}"

app.run()
```

However, manually returning can be messy. For this, view.py provides you the `Error` class, which behaves like an `Exception`. It takes two parameters:

-   The status code, which is `400` by default.
-   The message to send back to the user. If this is `None`, it uses the default error message (e.g. `Bad Request` for error `400`).

Since `Error` works like a Python exception, you can `raise` it just fine:

```py
from view import new_app, Error

app = new_app()

@app.get("/")
async def index(number: int):
    if number == 1:
        raise Error(400)

    return f"your number is {number}"

app.run()
```

!!! warning

    `Error` can only be used to send back *error* responses. It can **not** be used to return status codes such as `200`.

## Caching

Sometimes, computing the response for a route can be expensive or unnecessary. For this, view.py, along with many other web frameworks, provide the ability to cache responses.

View lets you do this by using the `cache_rate` parameter on a router.

For example:

```py
from view import new_app

app = new_app()

@app.get("/", cache_rate=10)  # reload this route every 10 requests
async def index():
    return "..."

app.run()
```

You can see this in more detail by using a route that changes it's responses:

```py
from view import new_app

app = new_app()
count = 1

@app.get("/", cache_rate=10)
async def index():
    global count
    count += 1
    return str(count)

app.run()
```

In the above example, `index` is only called every 10 requests, so after 20 calls, `count` would be `2`.

## Response Protocol

If you have some sort of object that you want to wrap a response around, view.py gives you the `__view_result__` protocol. The only requirements are:

-   `__view_result__` is available on the returned object (doesn't matter if it's static or instance)
-   `__view_result__` returns data that corresponds to the allowed return values.

For example, a type `MyObject` defining `__view_result__` could look like:

```py
from view import new_app

app = new_app()

class MyObject:
    def __view_result__(self):
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

-   `Response` is simply a wrapper around other responses.
-   `HTML` is for returning HTML content.
-   `JSON` is for returning JSON content.

A common use case for `Response` is wrapping an object that has a `__view_result__` and changing one of the values. For example:

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

Note that **all response classes inherit from `Response`**, meaning you can use this functionality anywhere.

!!! note

    A `Response` must be *returned* for things like `cookie` to take effect. For example:

    ```py
    from view import new_app, Response

    app = new_app()

    @app.get("/")
    async def index():
        res = Response(...)
        return "..."  # res is not returned!

    app.run()
    ```

### Body Translate Strategy

The body translate strategy in the `__view_result__` protocol refers to how the `Response` class will translate the body into a `str`. There are four available strategies:

-   `str`, which uses the object's `__str__` method.
-   `repr`, which uses the object's `__repr__` method.
-   `result`, which calls the `__view_result__` protocol implemented on the object (assuming it exists).
-   `custom`, uses the `Response` instance's `_custom` attribute (this only works on subclasses of `Response` that implement it).

For example, the route below would return the string `"'hi'"`:

```py
from view import new_app, Response

app = new_app()

@app.get("/")
async def index():
    res = Response('hi', body_translate="repr")
    return res

app.run()
```

### Implementing Responses

`Response` is a [generic type](https://mypy.readthedocs.io/en/stable/generics.html), meaning you should supply it a type argument when writing a class that inherits from it.

For example, if you wanted to write a type that takes a `str`:

```py
class MyResponse(Response[str]):
    def __init__(self, body: str) -> None:
        super().__init__(body)
```

Generally, you'll want to use the `custom` translation strategy when writing custom `Response` objects.

You must implement the `_custom` method (which takes in the `T` passed to `Response`, and returns a `str`) to use the `custom` strategy. For example, the code below would be for a `Response` type that formats a list:

```py
from view import Response

class ListResponse(Response[list]):
    def __init__(self, body: list) -> None:
        super().__init__(body, body_translate="custom")

    def _custom(self, body: list) -> str:
        return " ".join(body)
```

## Middleware

### What is middleware?

In view.py, middleware is called right before the route is executed, but **not necessarily in the middle.** However, for tradition, View calls it middleware.

The main difference between middleware in view.py and other frameworks is that in view.py, there is no `call_next` function in middleware, and instead just the arguments that would go to the route.

!!! question "Why no `call_next`?"

    view.py doesn't use the `call_next` function because of the nature of it's routing system.

### The Middleware API

`Route.middleware` is used to define a middleware function for a route.

```py
from view import new_app

app = new_app()

@app.get("/")
async def index():
    ...

@index.middleware
async def index_middleware():
    print("this is called before index()!")

app.run()
```

## Review

Responses can be returned with a string, integer, and/or dictionary in any order.

-   The string represents the body of the response (e.g. the HTML or JSON)
-   The integer represents the status code (200 by default)
-   The dictionary represents the headers (e.g. `{"x-www-my-header": "some value"}`)

`Response` objects can also be returned, which implement the `__view_result__` protocol. All response classes inherit from `Response`, which supports operations like setting cookies.

Finally, the `middleware` method on a `Route` can be used to implement middleware.
