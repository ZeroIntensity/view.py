# Configuration

## Introduction

Before you can make any projects with view.py, you should learn about how it handles configuration. Configuration is handled by the [configzen](https://github.com/bswck/configzen) library under the hood, so most questions about configuration will be answered there.

## The Config File

When creating your app, view will search for one of the following configuration files:

- `view.toml`
- `view.json`
- `view.ini`
- `view_config.py`

Note that while all of these are different formats, they can all evaluate to the same thing internally. If you have any questions on these semantics, once again see [configzen](https://github.com/bswck/configzen).

## Programatically

Many Python users aren't fond of the configuration file strategy, and that's okay. View supports editing the config at runtime just fine through the `config` property. The `config` property stores a `Config` object, which holds more subcategories.

```py
app = new_app()
app.config.foo.bar = "..."
```

::: view.config.Config

## Settings

View has several different configuration settings. For documentation purposes, values will be talked about in terms of Python (i.e. `null` values will be regarded as `None`).

At the top level, there's one real setting: `dev`.

`dev` is `True` by default, and is what tells view.py whether you're running in a production server setting or just running on your local machine.

### App Settings

- `loader`: This is the strategy that will be used to load routes. Can be `manual`, `simple`, or `filesystem`. `manual` by default.
- `app_path`: A string defining the location of the app, as well as the variable name. Should be in the format of `file_path:variable_name`. `app.py:app` by default.
- `uvloop`: Whether or not to use `uvloop` as a means of event loop. Can be `decide` or a `bool` value. `decide` by default.
- `loader_path`: When the loader is `simple` or `filesystem`, this is the path that it searches for routes. `routes/` by default.

## Server Settings

- `host`: IPv4 address specifying what address to bind the server to. `0.0.0.0` by default.
- `port`: Integer defining what port to bind the server to. `5000` by default.
- `backend`: ASGI backend to use. Only `uvicorn` is supported as of now.
- `extra_args`: Dictionary containing extra parameters for the ASGI backend. This parameter is specific to the backend (only `uvicorn`, as of now) and not view.

## Log Config

- `level`: Log level. May be `debug`, `info`, `warning`, `error`, `critical`, or an `int`. This is based on Python's built-in [logging module](https://docs.python.org/3/library/logging.html). `info` by default.
- `hijack`: This is a `bool` value defining whether or not to "hijack" the ASGI backend's logger and convert it to view.py's logging style. `True` by default.
- `fancy`: Whether to use View's fancy output mode. `True` by default.
- `pretty_tracebacks`: Whether to use [Rich Exceptions](https://rich.readthedocs.io/en/stable/logging.html?highlight=exceptions#handle-exceptions). `True` by default.
