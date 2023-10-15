# Development Workflow

## Getting Started

To get started with developing view.py, clone the repo via git:

```
$ git clone https://github.com/ZeroIntensity/view.py && cd view.py
```

Next, create a branch for your feature or contribution:

```
$ git branch my-idea
$ git checkout my-idea
```

If you're too lazy to come up with a name, just name it after the issue:

```
$ git branch impl-24
```

## Installation and running

Once you have view.py cloned locally, you need to be able to run your code somehow. I like to follow the `test.py` workflow, where you work with the code locally and then write the tests after you're done. This saves a lot of time as you don't have to wait on `pip install` every time you make a change.

A `test.py` would look like this for me:

```py
from src.view import whatever

# ...
```

Or, if you don't like the `from x import y` approach, you can do:

```py
import src.view as view
```

Now, once you've written all your code, you should write the tests for it, but more on that later. To install your version of view.py, run `pip install .` inside the directory.

### C Extension

While trying to run view.py locally for the first time, you may get an error saying `_view has not been built`, but what is `_view`?

`_view` is the name of the C extension module. It contains all the logic for the actual ASGI app and async things. `_view` gets compiled every time you install the project locally (i.e. `pip install .`), so you need to do that at least once to get it running.

## Tests

view.py uses `ward` as a means of testing. To write a test, see [their docs](https://ward.readthedocs.io). Note that the tests import from `view` and not `src.view`, so you do install to reinstall the local project (`pip install .`) in order to update the code there.

In view.py, a test could look like this:

```py
@test("my awesome feature")
async def _():
    app = new_app()

    # ...
```

### Testing Apps

In tests, **do not call `run()`.** Instead, use `App.test()`, which uses a virtual ASGI server to test responses from a route without actually starting a server.

`test()` is an async context manager and returns `view.app.TestingContext`. It can be used like so:

```py
@test("my awesome feature")
async def _():
    app = new_app()

    async with app.test() as test:
        res = await test.get("/", query={"hello": "world"}, body={"goodbye": "world"})
```

In the above, we use `get()` as an example, but all other HTTP methods (i.e. `post()`, `put()`, `patch()`) are supported just fine.
