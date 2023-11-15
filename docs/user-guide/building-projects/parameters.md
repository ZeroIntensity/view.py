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

There is little to no difference between the standard and direct variations, **including loading**. The direct versions are only to be used when the app is already available to **prevent extra imports**.

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

The `query()` call can actually come before `get` due to the nature of the routing system. In fact, anything you decorate a route with does not have specific order needed. For example, the following is completely valid:

```py
@app.query("hello", int)  # query comes before get()
@app.get("/")
async def index(hello: int):
    ...
```

## Cast Semantics

In query strings, only a string can be sent, but these strings can represent other data types. This idea is called **casting**, and it's not at all specific to Python. If you're still confused, think of it like calling `int()` on the string `"1"` to convert it into an integer `1`.

View has this exact same behavior when it comes to route inputs. If you tell your route to take an `int`, view.py will do all the necessary computing internally to make sure that you get an integer in your route. If a proper integer was not sent, then the server will automatically return an error `400` (Bad Request). There are a few things that should be noted for this behavior:

- Every type can be casted to `str`.
- Every type can be casted to `Any`.
- `bool` expects `true` and `false` (instead of Python's `True` and `False`) to fit with JSON's types.
- `dict` expects valid JSON, **not** a valid Python dictionary.

## Typing Inputs

Typing route inputs is very simple if you're already familiar with Python's type annotation system. Again, unions can be formed via passing multiple types instead of one. However, direct union types provided by Python are supported too. This includes both `typing.Union` and the newer `|` syntax.

```py
from view import new_app
from typing import Union

app = new_app()

@app.get("/")
@app.query("name", str, int)
async def index(name: str | int):
    ...

@app.get("/hello")
@app.query("name", Union[str, int])
async def hello(name: str | int):
    ...

@app.get("/world")
@app.query("name", str | int)
async def world(name: str | int):
    ...

app.run()
```

The types supported are (all of which can be mixed and matched to your needs):

- `str`
- `int`
- `bool`
- `list` (or `typing.List`)
- `dict` (or `typing.Dict`)
- `Any` (as in `typing.Any`)
- `None`
- `dataclasses.dataclass`
- `pydantic.BaseModel`
- `typing.NamedTuple`
- `typing.TypedDict`
- Any object supporting the `__view_body__` protocol.

### Lists and Dictionaries

You can use lists and dictionaries in a few ways, the most simple being just passing the raw type (`list` and `dict`). In typing terms, view.py will assume that these mean `dict[str, Any]` (as all JSON keys have to be strings) and `list[Any]`. If you would like to enforce a type, simply replace `Any` with an available type. The typing variations of these types (`typing.Dict` and `typing.List`) are supported as well.

```py
from view import new_app
from typing import Dict

app = new_app()

@app.get("/")
@app.query("name", Dict[str, str | int])
async def index(name: Dict[str, str | int]):
    ...

@app.get("/hello")
@app.query("name", dict)
async def hello(name: dict):
    ...

app.run()
```

Note that backport is **not possible** if you're using new typing features (such as the `dict[...]` or `list[...]`) as `from __future__ import annotations` does not affect parameters, meaning that the second value sent to the route input function (again, `query` or `body`) is not changed.

## Using Objects

As listed about earlier, view.py supports a few different objects to be used as types. All of these objects are meant for holding data to a specific model, which can be incredibly useful in developing web apps. Some things should be noted when using these types:

- Any annotated value types must an available type already (i.e. `str | int` is supported, but `set | str` is not). Other objects are indeed supported.
- Respected modifiers are supported (such as `dataclasses.field` on `dataclass`).
- Methods are unrelated to the parsing, and may return any type and take any parameters. Methods are not accessible to the user (as JSON doesn't have methods).

Here's an example using `dataclasses`:

```py
from view import new_app
from dataclasses import dataclass, field
from typing import List

app = new_app()

@dataclass
class Person:
    first: str
    last: str
    favorite_foods: List[str] = field(default_factory=list)

@app.get("/")
@app.query("me", Person)
async def index(me: Person):
    return f"Hello, {me.first} {me.last}"
```

If you would prefer to not use an object, view supports using a `TypedDict` to enforce parameters. It's subject to the same rules as normal objects, but is allowed to use `typing.NotRequired` to omit keys. Note that `TypedDict` **cannot** have default values.

```py
from view import new_app
from typing import TypedDict, NotRequired, List

app = new_app()

class Person(TypedDict):
    first: str
    last: str
    favorite_foods: NotRequired[List[str]]

@app.get("/")
@app.query("me", Person)
async def index(me: Person):
    return f"Hello, {me['first']} {me['last']}"
```

## Body Protocol

If any of the above types do not support your needs, you may design your own type with the `__view_body__` protocol. On a type, `__view_body__` can be held in one of two things:

- An attribute (e.g. `cls.__view_body__ = ...`)
- A property
- A static (or class) method.

Whichever way you choose, the `__view_body__` data must be accessed statically, **not in an instance**. The data should be a dictionary (containing only `str` keys, once again), but the values should be types, not instances. These types outline how view.py should parse it at runtime. For example, a `__view_body__` to create an object that has a key called `a`, which a `str` value would look like so:

```py
class MyObject:
    __view_body__ = {"a": str}
```

View **does not** handle the initialization, so you must define a proper `__init__` for it. If you are already using the `__init__` for something else, you can define a `__view_construct__` class or static method and view.py will choose it over `__init__`.

```py
class MyObject:
    __view_body__ = {"a": str}

    @classmethod
    def __view_construct__(cls, **kwargs):
        self.a: str = kwargs["a"]
```

### Default Types and Unions

`__view_body__` works the same as standard object types would work in the sense that types like `typing.Union` or the `|` syntax are supported, but you may also use a special value called `BodyParam`. `BodyParam` will allow you to pass union types in a tuple and set a default value. If you only want one type when using `BodyParam`, simply set `types` to a single value instead of a tuple. Here's an example of how it works, with the original object from above:

```py
class MyObject:
    __view_body__ = {
        "a": view.BodyParam(types=(str, int), default="hello"),
        "b": view.BodyParam(types=str, default="world"),
    }

    @classmethod
    def __view_construct__(cls, **kwargs):
        self.a: str | int = kwargs["a"]
        self.a: str = kwargs["b"]
```

## Client Semantics

On the client side, sending data to view.py might be a bit unintuitive. For this part of the documentation, a JSON body will be used for simplicity. In the case of JSON, strings will be casted to a proper type if the route supports it. For example, if a route takes `a: str | int`, the following would be set to the integer `1`, not `"1"`.

```json
{
    "a": "1"
}
```

Objects are simply formatted in JSON as well. If you had an object under the parameter name `test` and that object had the key `a: str`, it would be sent to the server like so:

```py
{
    "test": {
        "a": "..."
    }
}
```
