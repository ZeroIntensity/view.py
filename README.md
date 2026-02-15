<div align="center">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ZeroIntensity/view.py/main/logos/logo_theme_dark.png" alt="view.py logo (dark)"  width=450 height=auto>
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/ZeroIntensity/view.py/main/logos/logo_theme_light.png" alt="view.py logo (light)"  width=450 height=auto>
      <img alt="view.py logo">
    </picture>
</div>

<div align="center"><h2>The Batteries-Detachable Web Framework</h2></div>

This is a work-in-progress!

## Installation

It's highly recommended to install from source at the moment:

```
$ pip install git+https://github.com/zerointensity/view.py
```

## Example

```py
from view.core.app import App

from view.dom.core import html_response
from view.dom.components import page
from view.dom.primitives import h1

app = App()


@app.get("/")
@html_response
async def home():
    with page("Hello, view.py!"):
        yield h1("Nobody expects the Spanish Inquisition")


app.run()
```

## Copyright

`view.py` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
