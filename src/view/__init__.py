# flake8: noqa
"""
view.py - The Batteries-Detachable Web Framework

Docs: https://view.zintensity.dev
GitHub: https://github.com/zerointensity/view.py
Support: https://github.com/sponsors/ZeroIntensity

Quickstart:

```py
from view import new_app

app = new_app()

@app.get("/")
def index():
    return "Hello, view.py!"

app.run()
```
"""
try:
    import _view
except ModuleNotFoundError as e:
    raise ImportError(
        "the _view extension module is missing! view.py cannot be used with pure python"
    ) from e

# these are re-exports
from _view import Context, HeaderDict, InvalidStatusError

from .__about__ import *
from .app import *
from .build import *
from .default_page import *
from .exceptions import *
from .integrations import *
from .logging import *
from .patterns import *
from .response import *
from .routing import *
from .templates import *
from .typecodes import *
from .util import *
from .ws import *
