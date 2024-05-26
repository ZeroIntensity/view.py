---
hide:
    - navigation
---

# Welcome to view.py's documentation!

Here, you can learn how to use view.py and its various features.

-   [Source](https://github.com/ZeroIntensity/view.py)
-   [PyPI](https://pypi.org/project/view.py)
-   [Discord](https://discord.gg/tZAfuWAbm2)

## Showcase

```py
from view import new_app

app = new_app()

@app.get("/")
async def index():
    return await app.template("index.html", engine="jinja")

app.run()
```

```py
# routes/index.py
from view import get, HTML

# Build TypeScript Frontend
@get(steps=["typescript"], cache_rate=1000)
async def index():
    return await HTML.from_file("dist/index.html")
```

```py
from dataclasses import dataclass
from view import body, post

@dataclass
class User:
    name: str
    password: str

@post("/signup")
@body("data", User)
def create(data: User):
    # Use database of your choice...
    return JSON({"message": "Successfully created your account."}), 201
```

```py
from view import new_app, Context, Error, JSON

app = new_app()

@app.get("/")
@app.context
async def index(ctx: Context):
    auth = ctx.headers.get("Authorization")
    if not auth:
        raise Error(400)

    return JSON({"data": "..."})

app.run()
```

```py
from view import new_app

app = new_app()

@app.post("/login")
@app.query("username", doc="Username for your account.")
@app.query("password", doc="Password for your account.")
async def index():
    """Log in to your account."""
    ...

app.run()
```

```html
<view if="user.type == 'admin'">
    <view template="admin_panel" />
</view>
<view elif="user.type == 'moderator'">
    <view template="mod_panel" />
</view>
<view else>
    <p>You must be logged in.</p>
</view>
```

```toml
# view.toml
[build]
default_steps = ["nextjs"]
# Only NextJS will be built on startup

[build.steps.nextjs]
requires = ["npm"]
command = "npm run build"

[build.steps.php]
requires = ["php"]
command = "php -f payment.php"
```

## Why did I build it?

!!! warning

    This section may seem boring to some. If you don't like reading, skip to the next page.

This is a question I get a lot when it comes to view.py. I originally got the idea for view.py back in 2021, but it was planned to be a library for _only_ designing UI's in Python (hence the name "view"), since the only way you could do it at the time was pretty much just merging HTML and Python using [Jinja](https://jinja.palletsprojects.com/en/3.1.x/), or some other flavor of template engine. Don't get me wrong, Jinja is a great template engine, but it feels a bit lacking once you've tried [JSX](https://react.dev/learn/writing-markup-with-jsx) in one of the large JavaScript frameworks.

A year later, in 2022, I enrolled in a coding class at my school, which was basically a course for the basics of Python. For most Python developers, including me, it would have felt like sitting down and going over your ABC's. Long story short, my teacher let me do some sort of project instead of the actual class (this was in 8th grade, mind you).

At the time, my [pointers.py](https://github.com/ZeroIntensity/pointers.py) library had gained a lot of traction on GitHub, which was quite cool to me, but I felt like I didn't make any real world contributions (it is a joke library, anyway). I wanted to contribute something to the world, and since I was being allocated school time during the week to work on a project of my choice, I decided that a full web framework was what I wanted to do.

In my eyes, Python's web ecosystem was nowhere near that of JavaScript's. I had grown particularly fond of [NextJS](https://nextjs.org/), which served as an inspiration for a lot of view.py's features. To this day, [FastAPI](https://fastapi.tiangolo.com/) remains as my favorite Python web framework, apart from View. In fact, if you don't like view.py, I highly recommend trying it. Anyways, at the time, FastAPI was somewhat lacking when it comes to batteries-included parts, compared to [Django](https://www.djangoproject.com/), at least.

Now, this opinion is a bit controversial, but I really don't like Django's approach to a lot of things (such as it's way of routing), as well as the massive boilerplate that comes with Django projects. It just doesn't feel [pythonic](https://ifunny.co/picture/other-programmers-python-programmer-that-s-not-the-most-pythonic-EUE0IBzz8) to me. Although, what I do admire about Django (and probably why so many people like it), is it's batteries-included philosophy. So, I wanted to develop a web framework with the speed and elegancy of FastAPI, with the sheer robust-ness of Django. view.py is the result of that idea.

Note that I don't want to replace Django or FastAPI. In fact, if you're already familiar with one of those, learning view.py might not be a good idea! However, I would like to fill the gap that you might feel when using a Python framework after coming from JavaScript. Nowadays, JavaScript web frameworks get rewritten every year (for example, Next's move from `pages` to the `app` router), and are filled with big companies fighting each other to "be the best." In my eyes, development in all fields, especially open source, should be _collaborative_, not competitive, and I'm glad that Python has stayed true to that, but the gap in web development is visible.
