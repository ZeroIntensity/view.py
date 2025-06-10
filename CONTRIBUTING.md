# Contributing

**Thanks for wanting to contribute to view.py!**

view.py is very new and is under heavy development. Whether you're completely new to GitHub contribution or an experienced developer, view.py has something you could help out with. If you want to jump right in, the [issues tab](https://github.com/ZeroIntensity/view.py/labels/beginner) has plenty of good starts.

If you're stuck, confused, or just don't know what to start with, our [Discord](https://discord.gg/tZAfuWAbm2) is a great resource for questions regarding the internal mechanisms or anything related to view.py development. If you are actively working on an issue, you may ask for the contributor role (assuming it wasn't given to you already).

## Getting Started

Assuming you have Git installed, simply clone the repo and install view.py locally (under a virtual environment):

```
$ git clone https://github.com/ZeroIntensity/view.py
$ cd view.py
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install .
```

Congratulations, you have just started your development with view.py!

Note that this cannot be an editable install (the `-e` flag), as `scikit-build-core` does not support it.

## Workflow

First, you should create a new branch:

```
$ git switch -c my-cool-feature
```

All of your code should be contained on this branch.

Generally, a simple `test.py` file that starts a view app will be all you need. For example, if you made a change to the router, a way to test it would be:

```py
from view import new_app

app = new_app()

@app.get("/", some_cool_feature_you_made='...')
async def index():
    return "Hello from view.py locally!"

app.run()
```

Note that you do need to `pip install .` to get your changes under the `view` module. However, waiting for pip every time can be a headache. Unless you're modifying the [C API](https://github.com/ZeroIntensity/view.py/tree/master/src/_view), you don't actually need it. Instead, you can test your code via just importing from `src.view`. A `test.py` file **should not** be inside of the `src/view` folder, but instead outside it (i.e. in the same directory as `src`).

For example, a simple `test.py` could look like:

```py
# test.py
from src.view import new_app

app = new_app()

@app.get("/")
async def index():
    return "Hello from view.py locally!"

app.run()
```

**Note:** Import from `view` internally _does not_ work when using `src.view`. Instead, your imports inside of view.py should look like `from .foo import bar`. For example, if you wanted to import `view.routing.get` from `src/view/app.py`, your import would look like `from .routing import get`

For debugging purposes, you're also going to want to disable `fancy` and `server_logger` in the configuration:

```toml
[log]
fancy = false
server_logger = true
```

These settings will stop view.py's fancy output from showing, as well as stopping the hijack of the server's logger, and you'll get the raw server output.

## Writing Tests

**Note:** You do need to `pip install .` to update the tests, as they import from `view` and not `src.view`.

View uses [pytest](https://docs.pytest.org/en/8.2.x/) for writing tests, as well as [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/latest/) and [pytest-memray](https://pytest-memray.readthedocs.io/en/latest/). If you have any questions regarding test semantics, it's likely on their docs. The only thing you need to understand for writing tests is how to use the `App.test` API.

`App.test` is a method that lets you start a virtual server for testing responses. It works like so:

```py
async def test_my_feature():
    app = new_app()

    @app.get("/")
    async def index():
        return "test"

    async with app.test() as test:
        res = await test.get("/")
        assert res.message == "test"
```

In the above code, a server **would not** be started, and instead just virtualized for testing purposes.

## Updating the changelog

View follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), so nothing fancy is needed for updating changelogs. Don't put your code under a version, and instead just keep it under the `Unreleased` section.

## Merging your code

Now that you're done writing your code and want to share it with the world of view.py, you can make a pull request on GitHub. After tests pass, your code will be merged.

**Note:** Your code will not be immediatly available on PyPI, as view.py doesn't create a new release automatically. When the release is ready (which might take time), your code will be available under the [view.py package](https://pypi.org/project/view.py) on PyPI.
