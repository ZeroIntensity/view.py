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

## Response Objects



### Cookies

## Components
