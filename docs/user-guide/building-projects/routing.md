# Routing

## Loaders

Routing is a big part of any web library, and there are many ways to do it. View does it's best to support as many methods as possible to give you a well rounded approach to routing. In view, your choice of routing is called the loader/loader strategy, and there are three of them:

- `manual`
- `simple`
- `filesystem`

### Manually Routing

If you're used to Python libraries like [Flask](https://flask.palletsprojects.com/en/3.0.x/) or [FastAPI](https://fastapi.tiangolo.com), then you're probably already familiar with manual routing. Manual routing is considered to be letting the user do all of the loading themself, and not do any automatic import or load mechanics. There are two ways to do manual routing, directly calling on your `App` being the most robust. Here's an example:

```py
from view import new_app

app = new_app()

@app.get("/")
def index():
    return "Hello, view.py!"

app.run()
```

This type of function is called a **direct router**, and is what's recommended for small view.py projects. However, if you're more accustomed to JavaScript libraries, using the **standard routers** may be a good fit. When using manual routing, a standard router must be registered via a call to `App.load`.

```py
from view import new_app, get

app = new_app()

@get("/")
def index():
    return "Hello, view.py!"

app.load([get])
app.run()
```

This method may be a bit more versatile if you plan on writing a larger project using manual routing, as you can import your routes from other files, but if that's the case it's recommended that you use one of the other loaders.

### Simple Routing

Simple routing is similar to manual routing, but you tend to not use direct routers and don't have any call to `load()`. In your routes directory (`routes/` by default, `loader_path` setting), your routes will be held in any number of files. Simple loading is recursive, so you may also use folders. View will automatically extract any route objects created in these files.

```py
# routes/foo.py
from view import get

@get("/foo")
def index():
    return "foo"

@get("/bar")
def bar():
    return "bar"
```
