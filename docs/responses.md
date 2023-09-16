# Responses

## Basics

view.py allows you to return three things from a route: the body, the headers, and the status code.

You can simply return these via a tuple:

```py
@app.get("/")
async def index():
    return "you are not worthy", 400, {"x-worthiness": "0"}
```

In fact, it can be in any order you want:

```py
@app.get("/")
async def index():
    return {"x-worthiness": "0"}, "you are not worthy", 400
```

### Result Protocol

If you need to return a more complicated object, you can put a `__view_result__` function on it:

```py
class MyObject:
    def __view_result__(self) -> str:
        return "123"

@app.get("/")
async def index():
    return MyObject()
```

## Components

### Using built-in components

You can import any standard HTML components from the `view.components` module:

```py
from view.components import html, title, head, body, h1
from view import new_app

app = new_app()

@app.get("/")
async def index():
    return html(
        head(
            title("Hello, view.py!"),
        ),
        body(
            h1("This is my website!"),
        ),
    )

app.run()
```

The above would translate to the following HTML snippet:

```html
<html>
    <head>
    <title>Hello, view.py!</title>
    <body>
        <h1>This is my website!</h1>
    </body>
</html>
```

#### Children

You can pass an infinite number of children to a component, and it will be translated to the proper HTML:

```py
div(p("a"), p("b"), p("c"))
```

Would translate to:

```html
<div>
    <p>a</p>
    <p>b</p>
    <p>c</p>
</div>
```

### Attributes

All built in components come with their respected attributes, per the HTML specification:

```py
@app.get("/")
async def index():
    return html(lang="en")
```

#### Classes

Since the `class` keyword is reserved in Python, view.py uses the parameter name `cls` instead:

```py
div(cls="hello")
```

### Custom Components

There's no need for any fancy mechanics when making a custom component, so you can just use a normal function:

```py
def my_header(content: str):
    return div(h1(content))
```

## Response Type

If you need to, you can use `view.Response` as an object wrapper for responses:

```py
import view

app = view.new_app()


@app.get("/")
async def index():
    res = view.Response("my response!")
    return res


app.run()
```

You may also easily use cookies with the response type:

```py
@app.get("/")
async def index():
    res = view.Response("my response!")
    res.cookie("hello", "world")
    return res
```

A response object may also be used to wrap a `__view_result__`, like so:

```py
class MyObject():
    def __view_result__(self):
        return "hello", 201

@app.get("/")
async def index():
    return view.Response(MyObject(), 200)  # Returns 200 instead of 201
```

### HTML Responses

While it's not required, the `view.HTML` type may come in handy if you're returning lots of HTML. You may pass 4 total types:

```py
view.HTML("<h1>Hi!</h1>")  # Renders HTML from a string
view.HTML(pathlib.Path("my_file.html"))  # Renders HTML from a file
view.HTML(view.html(...))  # Render HTML from a component

with open("my_file.html") as f:
    view.HTML(f)  # Render HTML from a file wrapper
```
