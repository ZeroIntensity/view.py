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
