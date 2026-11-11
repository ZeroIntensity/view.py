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

## Examples

### Simple Hello World

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

### Button Counter

```py
from view.core.app import App
from view.dom.core import html_response
from view.dom.components import page
from view.dom.primitives import button, p

from view.dom.javascript import CompileContext, javascript_compiler

app = App()


@javascript_compiler
def click_button(ctx: CompileContext) -> None:
    counter = ctx.document.get_element_by_id("counter")
    number = ctx.parse_int(counter.inner_html)
    number += 1
    counter.inner_html = number

    with ctx.condition(number == 42) as condition:
        with condition.if_true():
            ctx.window.alert("The answer!")
        with condition.if_false():
            ctx.console.log(number)


@app.get("/")
@html_response
async def home():
    with page("Counter"):
        yield p("0", id="counter")
        yield button("Click me!", onclick=click_button)


app.run()
```

JavaScript builders execute once when decorated and become strings. Use
`with ctx.condition(number < 10).while_true():` for a runtime loop. Conditions
containing calls can take a callback, for example
`ctx.condition(lambda: ctx.parse_int(counter.inner_html) < 10)`, so the calls
run on every iteration. Use `ctx.variable(expression)` to snapshot a value;
assign Python names to handles normally, and use `ctx.assign()` to replace
an existing JavaScript variable's value.

DOM lookups return typed, non-null elements and throw a JavaScript error if
the element is missing. Nullable APIs expose `.is_null()`, `.is_undefined()`,
and a checked `.unwrap()`. Additional browser APIs can use typed
`handle.get(name, result_type)`, `handle.set(name, value)`, and
`handle.call_method(name, *arguments, returns=result_type)`. Names in these
methods are JavaScript names. `ctx.expression(source, result_type)` and
`ctx.raw(source)` accept trusted JavaScript for syntax outside the typed API.

## Copyright

`view.py` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
