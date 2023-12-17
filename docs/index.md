<div align="center"><img src="https://raw.githubusercontent.com/ZeroIntensity/view.py/master/html/logo.png" alt="view.py logo" width=300 height=auto /></div>

## A new web framework for Python

- [Discord](https://discord.gg/tZAfuWAbm2)
- [Source](https://github.com/ZeroIntensity/view.py)
- [PyPI](https://pypi.org/project/view.py)

## Example

```py
from view import new_app, h1

@app.get("/")
def index():
    return h1("Hello, view.py!")

app.run()
```

## Quickstart

Install view.py:

```
$ pip install -U view.py
```

Initialize your project:

```
$ view init
```