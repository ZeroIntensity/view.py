# Welcome to view.py's documentation!

## Modern, lightning fast web framework

- [Source](https://github.com/ZeroIntensity/view.py)
- [PyPI](https://pypi.org/project/view.py)

## Example
```py
import view
from view.components import *

app = view.new_app()

@app.get("/")
async def index():
    return h1("Hello, view.py!")

@app.get("/hello/{name: str}")
async def hello(name: str):
    return p(f"Hello, {name}")

app.run()
```

## What's coming for view.py?

view.py is currently in a high alpha state, and many new features are on the way, such as:

- Seamless compilation of Python to JavaScript code
- JSX-like syntax (`<h1>"Hello, world"</h1>`)
- Database ORM's/DRM's

## Installation

### Linux/macOS

```
$ python3 -m pip install -U view.py
```

### Windows

```
> py -m pip install -U view.py
```

### From Source

```
$ git clone https://github.com/ZeroIntensity/view.py && cd view.py
$ pip install .
```

## Finalizing

Now, type `view` or `python3 -m view` (`py -m view` on Windows) to make sure everything is working:

```
$ view
Welcome to view.py!
Docs: https://view.zintensity.dev
GitHub: https://github.com/ZeroIntensity/view.py
```

**Note:** The remainder of this documentation will assume Python modules are on PATH and view.py may be executed with the raw `view` command.
