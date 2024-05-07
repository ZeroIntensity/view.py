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

