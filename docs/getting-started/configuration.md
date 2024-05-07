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

Configurations are loaded at runtime by the `load_config` function. If you would like to use View's configuration file without creating an `App`, you may use it like so:

```py
from view import load_config

config = load_config()
```

::: view.config.load_config

## Settings

View has several different configuration settings. For documentation purposes, values will be talked about in terms of Python (i.e. `null` values will be regarded as `None`).

At the top level, there's one real setting: `dev`.

`dev` is `True` by default, and is what tells view.py whether you're running in a production server setting or just running on your local machine.

### Environment Variables

If you would like to set a configuration setting via an [environment variable](https://en.wikipedia.org/wiki/Environment_variable), you must account for the setting's environment prefix.

All environment prefixes look like `view_<subcategory>_`. For example, the `loader` setting is under the `app` section, so to set `loader` you would use the following command:

```bash
$ export view_app_loader=filesystem
```

Environment variables can also be set via the `env` config setting, or by adding a `.env` file to the project:

```toml
[env]
TEST = "hello"
```

```.env
TEST=hello
```

You can access environment variables via the `view.env` utility:

```py
from view import env

test = env("TEST", tp=int)
# test will be an integer. if environment variable "TEST" does not  exist, an exception is thrown.
# if environment variable "TEST" is not an integer, an exception is thrown.
```

::: view.util.env

### App Settings

**Environment Prefix: `view_app_`**

| Key          | Description                                                                                                                    | Default      | 
| ------------ | ------------------------------------------------------------------------------------------------------------------------------ | ------------ |
| `loader`     | This is the strategy that will be used to load routes. Can be `manual`, `simple`, or `filesystem`.                             | `manual`     |
| `app_path`   | A string defining the location of the app, as well as the variable name. Should be in the format of `file_path:variable_name`. | `app.py:app` | 
| `uvloop`     | Whether or not to use `uvloop` as a means of event loop. Can be `decide` or a `bool` value.                                    | `decide`     |
| `loader_path`| When the loader is `simple` or `filesystem`, this is the path that it searches for routes.                                     | `routes/`    |

Example with TOML:

```toml
[app]
loader = "filesystem"
loader_path = "./app"
```

## Server Settings

*Environment Prefix:* `view_server_`

- `host`: IPv4 address specifying what address to bind the server to. `0.0.0.0` by default.
- `port`: Integer defining what port to bind the server to. `5000` by default.
- `backend`: ASGI backend to use. Only `uvicorn` is supported as of now.
- `extra_args`: Dictionary containing extra parameters for the ASGI backend. This parameter is specific to the backend (only `uvicorn`, as of now) and not view.

Example with TOML:

```toml
[server]
host = "localhost"
port = 8080
```

## Log Settings

*Environment Prefix:* `view_log_`

- `level`: Log level. May be `debug`, `info`, `warning`, `error`, `critical`, or an `int`. This is based on Python's built-in [logging module](https://docs.python.org/3/library/logging.html). `info` by default.
- `server_logger`: This is a `bool` determining whether the ASGI backend's logger should be displayed. `False` by default.
- `fancy`: Whether to use View's fancy output mode. `True` by default.
- `pretty_tracebacks`: Whether to use [Rich Exceptions](https://rich.readthedocs.io/en/stable/logging.html?highlight=exceptions#handle-exceptions). `True` by default.
- `startup_message`: Whether to show the view.py welcome message on server startup.

### User Logging Settings

*Environment Prefix:* `view_user_log_`

- `urgency`: The log level for user logging. `info` by default.
- `log_file`: The target file for outputting log messages. `None` by default.
- `show_time`: Whether to show the time in each message. `True` by default.
- `show_caller`: Whether to show the caller function in each message. `True` by default.
- `show_color`: Whether to enable colorization for messages. `True` by default.
- `show_urgency`: Whether to show the urgency for messages. `True` by default.
- `file_write`: The preference for writing to an output file, if set. May be `both`, to write to both the terminal and the output file, `only`, to write to just the output file, or `never`, to not write anything.
- `strftime`: The time format used if `show_time` is set to `True`. `%H:%M:%S` by default.

Example with TOML:

```toml
[log]
level = "warning"
fancy = false

[log.user]
log_file = "app.log"
```

## Template Settings

*Environment Prefix:* `view_templates_`

- `directory`: The path to search for templates. `./templates` by default.
- `locals`: Whether to include local variables in the rendering parameters (i.e. local variables can be used inside templates). `True` by default
- `globals`: The same as `locals`, but for global variables instead. `True` by default.
- `engine`: The default template engine to use for rendering. Can be `view`, `jinja`, `django`, `mako`, or `chameleon`. `view` by default.

Example with TOML:

```toml
[templates]
directory = "./pages"
engine = "jinja"
```
