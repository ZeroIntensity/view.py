# Creating An App

## Project Initialization

A new view.py project may be created via the `view init` command.

You will be prompted to select a path to initialize our app. For this example, let's use `my_app` (so if you were in `/root`, our app would be found in `/root/my_app`).

After this prompt, you will be asked for a loader strategy. More on this later, for now just set it to manual.

Here's what this should look like:

```
$ view init
Path to initialize to [./]: my_app
Loader strategy (manual, filesystem, simple) [filesystem]: manual
Created `view.toml`
Created `app.py`
Created `pyproject.toml`
Created `scripts`
Created `routes`
Created `routes/index.py`
Successfully initalized app in `/root/my_app`
```

## Standalone

Looking for a more simple approach with your app? Nothing that `view init` does is required, and you may just import and use view.py in any Python file like it were a minimalist such as [Flask](https://flask.palletprojects.com).

Example:

```py
from view import new_app

app = new_app()

# App content...

app.run()
```

## Loaders

If you chose the `view init` approach earlier, the CLI would have asked you to choose a loader, but what actually is that?

A loader is what tells view.py how to load your routes. There are a few loader options to choose from, which are `manual`, `simple`, and `filesystem`.

### Manual Loading

Manual is the simplest of the three, and you can pretty much figure it out just from it's name: an approach in which none of the route loading is done by view.

In the manual strategy, you have to import functions decorated with `@get()` and pass them into the `app.load()` call. However, this may seem tedious to some users, which means that you probably don't want to use this loader.

An example of manual loading could look like this:

```py
from view import new_app, get

app = new_app()

# Pretend that both index and about are in seperate files
@get("/")
async def index():
    return "..."

@get("/about")
async def about():
    return "..."

app.load((index, about))
app.run()

```

#### Directly Loading

In the example code above, this is actually not the best way to do it. We are decorating a route with view's `get` function to declare it as a route, but we don't need to do that. If your route is in the same file as your `app` (or you import it), then you can instead just call `app.get()` to avoid the `app.load()` call, like so:

```py
from view import new_app

app = new_app()

@app.get("/")
async def index():
    return "..."

# app.get automatically registers our route, no need for a call to load()
app.run()
```

I would generally recommend to use manual loading on very small apps with just a few pages, since `simple` and `filesystem` would actually generate more work to do in those scenarios.

### Simple Loading

Simple loading is roughly the same as manual, but instead of putting each route in a call to `app.load()`, files are just recursively checked for files in a routes directory (`your_app/routes` by default).

For example, your main `app.py` file could look like this:

```py
from view import new_app

app = new_app()
app.run()
```

But in a file called `routes/pages.py`, it could look like this:

```py
from view import get

@get("/")
async def index():
    return "..."


@get("/about")
async def about():
    return "..."
```

The routes above would be properly loaded by view.py without any need for a `load()` call.

Simple loading is probably the best option for most developers, but if you come from a different language, such as JavaScript, then the `filesystem` strategy may be for you.

### Filesystem Loading

If you've played with a framework like [Next](https://nextjs.org), then you may already understand what filesystem loading is. 

Filesystem loading uses the directory structure to decide how to define route names, so `./routes/login.py` would evaluate to the route `/login` in the browser. This tends to be looked down on by Python developers, but it can be quite handy when building web apps.

You can name a file `index.py` to give it the route name of the parent directory, so `/routes/something/index.py` would be `/something` in the browser.

An example of a filesystem routed file is like this:

```py
from view import get, post

# Notice how the path parameter in get() and post() is omitted
@get()
async def my_page():
    return "..."


@post()
async def my_post_page():
    return "..."
```

If you were to put this in a file under `routes/index.py`, `my_page` would be when `/` is requested in the browser, and `my_post_page` would be used when `POST /` is requested in the browser.

### Omitting Routes

If you would like to omit a file from being loaded by filesystem or simple loading, prefix it with a `_`. As an example, `my_page.py` would get loaded, but `_my_page.py` would not.

This could be useful is you want to hold a utilities file directly in your routes directory, but for that scenario the `scripts` directory is suggested instead.

## Acquiring the App

Sometimes you might have a case where you need to access the `App` instance, but trying to import it from your main file can be a headache because of circular import errors. view.py lets you get around this with the use of `get_app`.

Say this is your `app.py` code:

```py
# app.py
from view import new_app, get_app
from my_route import index

app = new_app()

app.load([index])
app.run()
```

And this is `my_route.py`:

```py
# my_route.py
from view import get
from app import app

@get("/")
async def index():
    return f"Running on {app.config.server.port}"
```

You would get an error, since both of these files try to import from each other. This can be a common problem when using an app.

To avoid this, view.py introduces the `get_app` function, which gets an `App` instance created by `new_app` and directly fetches it without an import:

```py
# my_route.py
from view import get, get_app

app = get_app()

@get("/")
async def index():
    return f"Running on {app.config.server.port}"
```
