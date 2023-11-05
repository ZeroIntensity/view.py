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

## From App

In a case where you have direct access to your `App` instance (i.e. in manual loading), you don't have to even use `body` and `query`, and instead use the app methods instead:

```py
@app.get("/hello")
@app.query("name", str)
async def hello(name: str):
    return f"hello, {name}"
```

`app.query` and `app.body` work exactly the same as `@query` and `@body`.

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
@app.query("number", int)
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
- `list` (or `typing.List`)
- `None`
- Pydantic Models
- Dataclasses
- `typing.TypedDict`
- `NamedTuple`

You can allow unions by just passing more parameters:

```py
@app.get('/hello')
@app.query("name", str, None)
async def hello(name: str | None):
    if not name:
        return "hello world"

    return f"hello {name}"
```

You can pass type arguments to a `dict`, which are also validated by the server:

```py
@app.get("/something")
@app.body("data", dict[str, int])  # typing.Dict on 3.8 and 3.9
async def something(data: dict[str, int]):
    # data will always be a dictionary of strings and integers
    return "..."
```

The key in a dictionary must always be `str` (i.e. `dict[int, str]` is not allowed), but the value can be any supported type (including other dictionaries!)

### Objects

Here's an example of using an object type with `dataclasses`:

```py
from view import new_app, query
from dataclasses import dataclass, field

app = new_app()

def now() -> str:
    ...  # Calculate current time

@dataclass
class Post:
    content: str
    created_at = field(default_factory=now)


@app.post("/create")
@app.query("data", Post)
async def create(data: Post):
    print(f"Created post {data.created_at}")
    return "Success", 201
```

You may also have recursive types, like so:

```py
class MyOtherObject(NamedTuple):
    something: int

class MyObject(NamedTuple):
    something: str
    another_thing: MyOtherObject
```

### Typed Dictionaries

You may use `typing.TypedDict` to type your dictionary inputs if you don't want to use a basic `dict[..., ...]` (or `typing.Dict`), like so:

```py
from view import new_app
from typing import TypedDict

app = new_app()

class MyDict(TypedDict):
    a: str
    b: int

@app.get("/")
@app.query("data", MyDict)
async def index(data: MyDict):
    return data["a"]

app.run()
```

You may also use `NotRequired` to allow certain keys to get omitted:

```py
class MyDict(TypedDict):
    a: str
    b: NotRequired[int]
```

## View Body Protocol

If you would like to create your own object that gets validated by view.py, you may use the `__view_body__` protocol.

A `__view_body__` should contain a dictionary containing the keys and their corresponding types, like so:

```py
from view import new_app

app = new_app()

class MyObject:
    __view_body__ = {"a": str, "b": int}

@app.get("/")
@app.query("data", MyObject)
async def index(data: MyObject):
    ...

app.run()
```

The above would ensure the body contains something like the following in JSON:

```json
{
    "data": {
        "a": "...",
        "b": 0
    }
}
```

A default type can be annotated via `view.BodyParam`:

```py
class MyObject:
    __view_body__ = {
        "hello": BodyParam(types=(str, int), default="world"),
        "world": BodyParam(types=str, default="hello"),
    }
```

Note that `__view_body__` can also be a static function, like so:

```py
class MyObject:
    @staticmethod
    def __view_body__():
        return {"a": str, "b": int}
```

### Initialization

By default, an object supporting `__view_body__` will have the proper keyword arguments passed to it's `__init__`.

If you would like to have special behavior in your `__init__`, you may instead add a static `__view_construct__` function that returns an instance:

```py
class MyObject:
    __view_body__ = {"a": str, "b": int}

    def __view_construct__(**kwargs):
        return MyObject()
```
