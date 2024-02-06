# Documenting Applications

## What is documenting?

Writing documentation (or "documenting", as view.py calls it) can be an important task when it comes to writing API's, but it can be extremely tedious to do manually. Other frameworks, such as [FastAPI](https://fastapi.tiangolo.com), have their own approaches to generating API documentation, a common  method is by using [OpenAPI](https://www.openapis.org/).

OpenAPI is a good choice when it comes to this topic, but View does not support it. However, [support is planned](https://github.com/ZeroIntensity/view.py/issues/103).

For now, View has it's own system internally that does not use OpenAPI. This means that **client generation is not yet supported.** If you would like to track this issue, see it [here](https://github.com/ZeroIntensity/view.py/issues/74).

## Writing Documentation

On a route, you may define a route's documentation in one of two ways:

- Passing `doc` to the router function (e.g. `@get("/", doc="Homepage")`)
- More versatile, adding a docstring to the route (e.g. `"""Homepage"""`)

Here's an example using both:

```py
from view import new_app

app = new_app()

@app.get("/", doc="The homepage")
async def index():
    ...

@app.get("/hello")
async def hello():
    """A greeting to the user."""

app.docs("docs.md")  # more on this function later
app.run()
```

## Documenting Inputs

For route inputs, it's almost idential, except that **you cannot** use a docstring, and instead must use the `doc` parameter. This syntax is the same across both `query` and `body` (including standard and direct).

```py
from view import new_app

@app.get('/')
@app.query("greeting", str, doc="The greeting to be used by the server", default="hello")
async def index(greeting: str):
    """The homepage that returns a greeting to the user."""
    return f"{greeting}, world!"
```

However, you may want to define documentation for certain object keys when using object types (i.e. they support `__view_body__` or are handled internally). In this case, you can use `typing.Annotated` and a docstring again

- The docstring defines a description for the overall class.
- `Annotated` can provide a description for a certain key.

```py
from view import new_app
from typing import Annotated, NamedTuple

app = new_app()

class Person(NamedTuple):
    """A person in the world."""
    first: Annotated[str, "Their first name."]
    last: Annotated[str, "Their last name."]

@app.get("/")
@app.query("person", Person)
async def index(person: Person):
    ...

app.run()
```

**Note:** If you are on Python 3.8, you will get an error complaining about `Annotated` not being a part of `typing`. In this case, you can import `Annotated` from `typing_extensions` instead.

## Autogeneration

View will generate your API documentation into a markdown document that you could render in something like [MkDocs](https://mkdocs.org). This can be done via `App.docs()`, which will generate the markdown and write it to a file for you.

There are, roughly speaking, two ways to write to a file via `App.docs()`:

- Passing it a `str` or `Path`.
- Passing it a `TextIO[str]` file wrapper.

```py
from view import new_app
from pathlib import Path

app = new_app()

app.docs("docs.md")
app.docs(Path("docs.md"))

with open("docs.md", "w") as f:
    app.docs(f)
```

Alternatively, you can also use the `view docs` command to generate your documentation:

```
$ view docs
- Created `docs.md`
```

::: view.app.App.docs

## Review

"Documenting" in terms of View, is the act of writing documentation. Other frameworks use [OpenAPI](https://www.openapis.org/) as a versatile solution to doing this, but [view.py does not yet support this](https://github.com/ZeroIntensity/view.py/issues/103).

To write a description for a route, you may pass a `doc` parameter to the router call, or instead add a docstring to the route function itself. In a route input, it's quite similar, where you pass `doc` to the input function, but **using a docstring is not allowed**.  However, this rule is broken in the case of using an object as the type. When using an object, you must provide a docstring to define the class's description, and use `typing.Annotated` (or `typing_extensions.Annotated`) to set descriptions for object attributes.

Finally, you can actually generate the markdown content via the `docs()` method on your `App`, or by the `view docs` command. `docs()` can take three types of parameters:

- A `str`, in which it opens the file path and attempts to write to it.
- A `Path`, in which the same thing happens.
- A `TextIO[str]` (file wrapper), where the file is **not opened** by View, and is instead just written to via the wrapper.
