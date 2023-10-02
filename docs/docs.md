# Documenting Your App

## Generating

You can take any view app and generate simple markdown docs for it via `app.docs`.

The behavior of `app.docs` is dependent on what arguments you pass it. If you pass it nothing, it will return the generated markdown as a string:

```py
from view import new_app

app = new_app()

# ...

my_docs = app.docs()
app.run()
```

If you pass it a `str` or `Path`, it will open and write to that file:

```py
app.docs("my_docs.md")
app.docs(Path("my_docs.md"))
app.run()
```

By default, `overwrite` is `True`, so it will overwrite the contents of the target file if it exists. To disable this behavior, simply set `overwrite` to `False`:

```py
app.docs("my_docs.md", overwrite=False)
app.run()
```


Finally, you may pass a file wrapper:

```py
with open("my_docs.md", "w") as f:
    app.docs(f)
```

## Documenting

If you were to generate docs for the average view app, there will be a lot of "No description provided" everywhere. So, how do we actually add descriptions?

To start, you can document a route via it's decorator, like so:

```py
from view import new_app

app = new_app()

@app.get("/", doc="Homepage!")
async def index():
    return "hello view.py"
```

You may also do it via the docstring:

```py
@app.get("/")
async def index():
    """Homepage."""
    return "hello view.py"
```

Both of these will do the same thing, except that the docstring version will show up in IDE or other documentation generators.

### Parameters

Documenting parameters can be done via the same `doc` parameter found above. For example, in a query:

```py
@app.get("/")
@app.query("data", str, doc="My data")  # works the same with body()
async def index(data: str):
    return "hello view.py"
```

It gets tricky when you have custom objects to take in parameters. To add a description for the overall type, add a docstring. For each object key, you use type hinting to your advantage. Pass your description as the second argument to `typing.Annotated` (or `typing_extensions.Annotated`), like this:

```py
from dataclasses import dataclass
from view import new_app

app = new_app()

@dataclass
class Person:
    """A person."""
    first: Annotated[str, "Your first name."]
    last: Annotated[str, "Your last name."]

@app.get("/")
@app.query("person", Person, doc="Your data.")
async def index(person: Person):
    """Homepage."""
    return f"Hello, {person.first} {person.last}"
```
