# App

`App` inherits from `_view`'s `ViewApp`, which is a base C class for defining the main ASGI entry point. More on that later, though. Most C app functions are called through accessing `self` inside of an `App` instance.

::: view.app.App

## Config

Configuration in view.py is handled by [configzen](https://github.com/bswck/configzen). For information about changing the config or how files are loaded, look at their docs.

Config loading is done by the `load_config` function in `config.py`. `load_config` searches through the possible paths that a configuration could be found (relative to the `path` and `directory` parameters passed to it).

The possible config filenames are as follows:

- `view.toml`
- `view.json`
- `view.ini`
- `view.yaml`
- `view_config.py`
- `config.py`

::: view.config.load_config

## App Creation

A new `App` instance takes in a `Config`, which is then used to handle behavior of the app. Upon creation of a new `App` instance, several attributes are set.

- `config`, which is the `Config` object passed.
- `_manual_routes` is a list containing routes passed to direct app route functions (i.e. `App.get` or `App.post`). This makes it easier on the end developer, since they don't have to manually `load()` their routes.
- `loaded`, which is just whether `load()` has been called.
- `running` is whether the app is started.
- `_docs` is a dictionary containing auto-docs information.
- `loaded_routes` is a list of all the loaded routes of the app. This is only populated after calling `load()`.

## Routing


