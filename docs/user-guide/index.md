# Welcome to view'py documentation!

In this documentation, you'll learn how to use view.py and it's various features.

## Quickstart

Install view.py:

```
$ pip install -U view.py
```

Initialize your project:

```
$ view init
```

**Note:** If this yields unexpected results, you may need to use `py -m view init` instead.

Write your first app:

```py
from view import new_app

app = new_app()

@app.query("greeting", str, default="hello")
@app.query("name", str, default="world")
@app.get("/")
async def index(greeting: str, name: str):
    return f"{greeting}, {name}!"
```

## Why View?

As of now, view.py is still in alpha. Lot's of development progress is being made, but a production-ready stable release is still a bit far off. With that being said, anything mentioned in this documentation has been deemed already stable. In that case, why choose view.py over other frameworks?

If you've used a framework like [Django](https://djangoproject.com), you're likely already familiar with the "batteries included" idea, meaning that it comes with everything you could need right out of the box. View takes a different approach: batteries-detachable. It aims to provide you everything you need, but gives you a choice to use it or not, as well as actively supporting external libraries. This ideology is what makes View special. In batteries detachable, you can use whatever you like right out of the box, but if you don't like View's approach to something or like another library instead, you may easily use it.

## Developing View

As stated earlier, view.py is very new and not yet at a stable 1.0.0 release. Whether you're completely new to GitHub contribution or an experienced developer, view.py has something you could help out with. If you're interested in contributing or helping out with anything, be sure to read [the contributors file](https://github.com/ZeroIntensity/view.py/blob/master/CONTRIBUTING.md).
