# Project Creation

## Automatic

The View CLI supports automatically creating a project via the `view init` command.

```
$ view init
```

The loader strategy is related to routing, which you will learn more about later.

## Manually

view.py doesn't actually need any big project structure. In fact, you can run an app in just a single Python file, but larger structures like this might be more convenient for big projects. The only real requirement for something to be a view app is that it calls `new_app`, but again, more on that later.

Some "hello world" code for manually starting a view project would look like this:

```py
from view import new_app

app = new_app()

@app.get("/")
def index():
    return "..."

app.run()
```

## Structure

First, in any view project, you need a file to contain your app. By default, view expects it to be in `app.py` under a variable called `app`. Again, you can change this via the `app_path` setting. You're also going to want an `app.run()` (assuming you named your `App` instance `app`), but more on that later.

```py
from view import new_app

app = new_app()
app.run()
```

Generally, you're going to want one of the configuration files talked about earlier, but if you're against configuration files that's OK, view.py will work just fine without it. If you choose to use something other than manual routing, you want a `routes` directory (unless you changed the `loader_path` setting).

```toml
# view.toml
dev = true

[app]
loader_path = "./my_custom_loader_path"
```

Finally, for mobility purposes, you may want to add a `pyproject.toml` that contains the dependencies for your project, in case you need to run your project on a different system.

```toml
# pyproject.toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "your_view_app"
requires-python = ">=3.8"
authors = [
  { name = "Your Name", email = "your@email.com" },
]
dependencies = ["view.py"]
```
