# Runtime Builds

## Static Exports

In some cases, you might want to export your application as [static HTML](https://en.wikipedia.org/wiki/Static_web_page). This makes it much easier to serve your app somewhere, at the limit of being able to perform actions server-side. You can export your app in view.py via the `view build` command, or by running the `build_app` function:

```
$ view build
* Starting build process!
* Starting build steps
* Getting routes
* Calling GET /...
* Created ...
* Created index.html
* Successfully built app
```

This will export your app into a static folder called `build`, which can then be served via something like [http.server](https://docs.python.org/3/library/http.server.html). An exported route cannot contain:

- Route Inputs
- Path Parameters
- A method other than `GET`

As stated above, you can also build your app programatically via `build_app`:

```py
from view import new_app
from view.build import build_app

app = new_app()
app.load()  # Call the loader manually, since we aren't calling run()

build_app(app)
```

## Build Steps

Instead of exporting static HTML, you might just want to call some build script at runtime for your app to use. For example, this could be something like a [Next.js](https://nextjs.org) app, which you want to use as the UI for your website. Each different build is called a **build step** in View.

To specify a build step, add it under `build.steps` in your configuration:

```toml
# view.toml
[build.steps.nextjs]
requires = ["npm"]
command = "npm run build"
```

By default, this will only be run once the app is started. If you would like to run it every time a certain route is called, add the `build` parameter to a router function. Note that this will make your route much slower (as a build process needs to be started for every request), so it's highly recommended that you [cache](https://view.zintensity.dev/building-projects/responses/#caching) the route.

For example:

```py
from view import new_app

app = new_app()

@app.get("/", build=["nextjs"], cache_rate=10000)  # Reloads app every 10,000 requests
async def index():
    return await app.template("out/index.html")

app.run()
```

## Default Steps

As said earlier, the default build steps are always run right before the app is started, and then never ran again (unless explicitly needed by a route). If you would like only certain steps to run, specify them with the `build.default_steps` value:

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

## Build Requirements

As you've seen above, build requirements are specified via the `requires` value. Out of the box, view.py supports a number of different build tools, compilers, and interpreters. To specify a requirement for one, simply add the name of their executable (*i.e.*, how you access their CLI). For example, since `pip` is accessed via using the `pip` command in your terminal, `pip` is the name of the requirement.

However, view.py might not support checking for a command by default (this is the case if you get a `Unknown build requirement` error). If so, you need a custom requirement. If you would like to, you can make an [issue](https://github.com/ZeroIntensity/view.py/issues] requesting support for it as well.

### Custom Requirements

There are four types of custom requirements, which are specified by adding a prefix to the requirement name:

- Importing a Python module (`mod+`)
- Executing a Python script (`script+`)
- Checking if a path exists (`path+`)
- Checking if a command exists (`command+`)

For example, the `command+gcc` would make sure that `gcc --version` return `0`:

```toml
# view.toml
[build.steps.c]
requires = ["command+gcc"]
command = "gcc *.c -o out"
```

### The Requirement Protocol

In a custom requirement specifying a module or script, view.py will attempt to call an asynchronous `__view_requirement__` function. This function should return a `bool` value, `True` indicating that the requirement exists, and `False` otherwise.

!!! note

    If no `__view_requirement__` function exists, then all view.py does it check that execution or import was successful, and marks the requirement as passing.

For example, if you were to write a requirement script that checks if the Python version is at least `3.10`, it could look like:

```py
# check_310.py
import sys

async def __view_requirement__() -> bool:
    # Make sure we're running on at least Python 3.10
    return sys.version_info >= (3, 10)
```

The above could actually be used via both `script+check_310.py` and `mod+check_310`. 

!!! tip

    Don't use the view.py build system to check the Python version or if a Python package is installed. Instead, use the `dependencies` section of a `pyproject.toml` file, or [PEP 723](https://peps.python.org/pep-0723/) script metadata.
