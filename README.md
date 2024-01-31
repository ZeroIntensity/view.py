<div align="center"><img src="https://raw.githubusercontent.com/ZeroIntensity/view.py/master/html/logo.png" alt="view.py logo" width=250 height=auto /></div>

<div align="center"><h2>The Batteries-Detachable Web Framework</h2></div>

> [!Warning]
> view.py is in very early stages and not yet considered to be ready for production.
> If you would like to follow development progress, join [the discord](https://discord.gg/tZAfuWAbm2).
> For contributing to view.py, please see our [CONTRIBUTING.md](https://github.com/ZeroIntensity/view.py/blob/master/CONTRIBUTING.md)

<div align="center">
    <a href="https://clientarea.space-hosting.net/aff.php?aff=303"><img width=250 height=auto src="https://cdn-dennd.nitrocdn.com/fygsTSpFNuiCdXWNTtgOTVMRlPWNnIZx/assets/images/optimized/rev-758b0f8/www.space-hosting.net/wp-content/uploads/2023/02/cropped-Icon.png"></a>
    <h3>view.py is affiliated with <a href="https://clientarea.space-hosting.net/aff.php?aff=303">Space Hosting</a></h3>
</div>

- [Docs](https://view.zintensity.dev)
- [Source](https://github.com/ZeroIntensity/view.py)
- [PyPI](https://pypi.org/project/view.py)
- [Discord](https://discord.gg/tZAfuWAbm2)

## Example

```py
from view import new_app, h1

app = new_app()

@app.get("/")
async def index():
    return h1("Hello, view.py!")

app.run()
```

## Installation

**Python 3.8+ is required.**

### Development 

```
$ pip install git+https://github.com/ZeroIntensity/view.py
```

### Linux/macOS

```
$ python3 -m pip install -U view.py
```

### Windows

```
> py -3 -m pip install -U view.py
```
