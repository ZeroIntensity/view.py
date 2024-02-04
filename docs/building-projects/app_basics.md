# App Basics

## New Applications

Every view project will have a `new_app` call. The simplest app looks like this:

```py
from view import new_app

app = new_app()
app.run()  # you'll learn about this later
```

`new_app` does a few important things:

-   Loads the configuration, regardless of whether a config file exists.
-   Sets the `App` address for use by `get_app` (more on that later).
-   Loads finalization code for when the app closes.

While it's not required for every app, naming your app variable `app` is the proper convention for view, as that's the default variable searched for when using the `view serve` command, but more on that in a moment.

For now, just try to stick with naming your app file `app.py` and your `view.App` instance `app`.

::: view.app.new_app

## Launching Apps

Python libraries generally have two ways to run a web server:

-   Running via the command line.
-   Launching from Python itself (e.g. a `server.start(...)` function).

Both have their benefits and downsides, so view.py supports both out of the box. `App` comes with its `run()` method, and the view CLI has the `view serve` command.

Generally, you're going to want to add an `app.run()` to every view.py project, like so:

```py
from view import new_app

app = new_app()
app.run()
```

This way, if you (or someone else) want to run your code programmatically, they can run it via something like `python3 app.py`. It's also more semantically clear that an app is going to start when you run that file.

If you prefer the CLI method, you can just run `view serve` and view.py will extract the app from the file itself, ignoring the `run()` call.

Note that this behavior is a double-edged sword, so be careful. When calling with `run()`, the Python script will never get past that line because the server will run indefinitely, but when using `view serve` it proceeds past it just fine since all it's doing is extracting the `app`, skipping `run()`. For example, take a look at this code:

```py
from view import new_app

app = new_app()
app.run()
print("you called the app with view serve")  # this only runs when `view serve` is used
```

### Fancy Mode

View comes with something called "fancy mode", which is a fancy UI that shows when you run the app. If you would like to disable this, you can do one of two things:

-   Disable the `fancy` setting in configuration.
-   Pass `fancy=False` to `run()`.

You should disable it in the configuration if you completely despise fancy mode and don't want to use it at all, but if you only want to temporarily turn it off (for example, if you're a view.py developer and need to see proper output) then pass `fancy=False`.

::: view.app.App.run

## Getting the App

### Circular Imports

If you've worked with big Python projects before, there's a good chance you've run into a circular import error. A circular import error occurs when two modules try to import each other. A view.py example of this problem would most likely be the main app file trying to import a route, but then that route tries to import the app.

!!! note

    The below example uses routing, which if you're reading this for the first time you don't know how to use yet. Focus on the use of the `app` variable and not the routing itself.

```py
# app.py
from view import new_app
from routes import my_route

app = new_app()
app.load([my_route])
app.run()
```

```py
# routes.py
from view import get
from app import app

@app.get("/something")
def something():
    return "something"

@get("/")
def index():
    return "Hello, view.py"
```

View gives you a solution to this problem: `get_app`. `get_app` uses some magic internally to get you your `App` instance right then and there, no import required. It works similar to how you would use `new_app`:

```py
from view import get_app

app = get_app()

@app.get("/")
def index():
    return "..."
```

::: view.app.get_app

## Review

Every view.py project should contain a call to `new_app`. `new_app` does important things like loading your configuration, set's up finalization code, and letting the `App` instance be used by `get_app`.

Running an app can be done in two ways: programmatically via the `App.run` or through `view serve` command. However, every view.py app should contain an `App.run` to give the choice for running programmatically. By default, view.py has a fancy UI when running your app, which may be disabled via editing the config or passing `fancy=False` to `run()`.

Finally, circular imports occur when two Python modules try to import each other, which can happen a lot in view when getting the app from the app file (especially in manual routing). To fix it, View provides a `get_app` function to get you your `App` instance without an import.
