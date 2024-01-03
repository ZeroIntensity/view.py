<div align="center"><img src="https://raw.githubusercontent.com/ZeroIntensity/view.py/master/html/logo.png" alt="view.py logo" width=250 height=auto /></div>

## The Batteries-Detachable Web Framework

> [!Warning]
> view.py is in very early stages and not yet considered to be ready for production.
> If you would like to follow development progress, join [the discord](https://discord.gg/tZAfuWAbm2).
> For contributing to view.py, please see our [CONTRIBUTING.md](https://github.com/ZeroIntensity/view.py/blob/master/CONTRIBUTING.md)

- [Docs](https://view.zintensity.dev)
- [Source](https://github.com/ZeroIntensity/view.py)
- [PyPI](https://pypi.org/project/view.py)
- [Discord](https://discord.gg/tZAfuWAbm2)

```py
from view import new_app, h1

app = new_app()

@app.get("/")
async def index():
    return h1("Hello, view.py!")

app.run()
```

### Installation

**Python 3.8+ is required.**

#### Linux/macOS

```
python3 -m pip install -U view.py
```

#### Windows

```
> py -3 -m pip install -U view.py
```
