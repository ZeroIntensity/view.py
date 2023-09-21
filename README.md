<div align="center"><img src="https://raw.githubusercontent.com/ZeroIntensity/view.py/master/html/logo.png" alt="view.py logo" width=200 height=auto /></div>

## Lightning fast, modern web framework

- [Docs](https://view.zintensity.dev)
- [Source](https://github.com/ZeroIntensity/view.py)
- [PyPI](https://pypi.org/project/view.py)
- [Discord](https://discord.gg/tZAfuWAbm2)

```py
import view
from view.components import h1

app = view.new_app()

@app.get("/")
async def index():
    return h1("Hello, view.py!")

app.run()
```

### Help! I have too much free time

Fear not! view.py is currently in a very high alpha stage of development, and always looking for new contributors. If you're interested, you can take a look at the [issues tab](https://github.com/ZeroIntensity/view.py/issues) or [CONTRIBUTING.md](https://github.com/Zerointensity/view.py/blob/master/CONTRIBUTING.md).

### Installation

**CPython 3.8+ is required.**

#### Linux/macOS

```
python3 -m pip install -U view.py
```

#### Windows

```
> py -3 -m pip install -U view.py
```
