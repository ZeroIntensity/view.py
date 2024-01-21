<div align="center"><img src="https://raw.githubusercontent.com/ZeroIntensity/view.py/master/html/logo.png" alt="view.py logo" width=250 height=auto /></div>
# Welcome to the view.py documentation!

Here, you can learn how to use view.py and its various features.

- [Source](https://github.com/ZeroIntensity/view.py)
- [PyPI](https://pypi.org/project/view.py)
- [Discord](https://discord.gg/tZAfuWAbm2)

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

app.run()
```

## Why View?

As of now, view.py is still in alpha. Lot's of development progress is being made, but a production-ready stable release is still a bit far off. With that being said, anything mentioned in this documentation has been deemed already stable. In that case, why choose view.py over other frameworks?

If you've used a framework like [Django](https://djangoproject.com), you're likely already familiar with the "batteries included" idea, meaning that it comes with everything you could need right out of the box. View takes a different approach: batteries-detachable. It aims to provide you everything you need, but gives you a choice to use it or not, as well as actively supporting external libraries. This ideology is what makes View special. In batteries detachable, you can use whatever you like right out of the box, but if you don't like View's approach to something or like another library instead, you may easily use it.

## Should I use it?

For a big project, **not yet**, as View is not currently ideal for working with a big codebase. However, **that doesn't mean you should forget about it**. view.py will soon be stable and production ready, and you should keep it in mind. To support view.py's development, you can either [sponsor me](https://github.com/sponsors/ZeroIntensity) or [star the project](https://github.com/zerointensity/view.py/stargazers).

## Developing View

As stated earlier, view.py is very new and not yet at a stable 1.0.0 release. Whether you're completely new to GitHub contribution or an experienced developer, view.py has something you could help out with. If you're interested in contributing or helping out with anything, be sure to read [the contributors file](https://github.com/ZeroIntensity/view.py/blob/master/CONTRIBUTING.md) and/or joining the [discord](https://discord.gg/tZAfuWAbm2).
