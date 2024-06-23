<div align="center">
    <picture>
      <source media="(prefers-color-scheme: dark)" src="https://raw.githubusercontent.com/ZeroIntensity/view.py/master/logo_theme_dark.png" alt="view.py logo (dark)"  width=250 height=auto>
      <source media="(prefers-color-scheme: light)" src="https://raw.githubusercontent.com/ZeroIntensity/view.py/master/logo_theme_light.png" alt="view.py logo (light)"  width=250 height=auto>
    </picture>
</div>

<div align="center"><h2>The Batteries-Detachable Web Framework</h2></div>

<div align="center">
    <img src="https://github.com/ZeroIntensity/view.py/actions/workflows/tests.yml/badge.svg" alt="Tests" width=auto height=auto />
    <img src="https://github.com/ZeroIntensity/view.py/actions/workflows/memory_check.yml/badge.svg" alt="Valgrind" width=auto height=auto />
    <img src="https://github.com/ZeroIntensity/view.py/actions/workflows/build.yml/badge.svg" alt="Build" width=auto height=auto />
</div>

> [!Warning]
> view.py is currently in alpha, and may be lacking some features.
> If you would like to follow development progress, be sure to join [the discord](https://discord.gg/tZAfuWAbm2).

-   [Docs](https://view.zintensity.dev)
-   [Source](https://github.com/ZeroIntensity/view.py)
-   [PyPI](https://pypi.org/project/view.py)
-   [Discord](https://discord.gg/tZAfuWAbm2)

## Features

-   Batteries Detachable: Don't like our approach to something? No problem! We aim to provide native support for all your favorite libraries, as well as provide APIs to let you reinvent the wheel as you wish.
-   Lightning Fast: Powered by [pyawaitable](https://github.com/ZeroIntensity/pyawaitable), view.py is the first web framework to implement ASGI in pure C, without the use of external transpilers.
-   Developer Oriented: view.py is developed with ease of use in mind, providing a rich documentation, docstrings, and type hints.

See [why I wrote it](https://view.zintensity.dev/#why-did-i-build-it) on the docs.

## Examples

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
from view import JSON, body, post

@post("/create")
@body("name", str)
@body("books", dict[str, str])
def create(name: str, books: dict[str, str]):
    # ...
    return JSON({"message": "Successfully created user!"}), 201
```

## There's C code in here, how do I know it's safe?

view.py is put through [rigorous testing](https://github.com/ZeroIntensity/view.py/tree/master/tests), checked with [Valgrind](https://valgrind.org/), and checks for memory leaks, thanks to [Memray](https://github.com/bloomberg/memray). See the testing badges at the top.

## Installation

**Python 3.8+ is required.**

### Development

```console
$ pip install git+https://github.com/ZeroIntensity/view.py
```

### PyPI

```console
$ pip install view.py
```

### Pipx

```console
$ pipx install view.py
```

## Copyright

`view.py` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

<div align="center">
    <a href="https://clientarea.space-hosting.net/aff.php?aff=303"><img width=150 height=auto src="https://cdn-dennd.nitrocdn.com/fygsTSpFNuiCdXWNTtgOTVMRlPWNnIZx/assets/images/optimized/rev-758b0f8/www.space-hosting.net/wp-content/uploads/2023/02/cropped-Icon.png"></a>
    <h4>view.py is affiliated with <a href="https://clientarea.space-hosting.net/aff.php?aff=303">Space Hosting</a></h4>
</div>
