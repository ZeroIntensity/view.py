# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

-   Added the `view docs` command
-   Reworked internal logging API and changed default logger format
-   Added the `websocket` router
-   Made hijack optional in fancy mode
-   Added a startup message
-   Added support for `daphne` and `hypercorn` as servers
-   Added documentation for `view.env` and added environment variables to configuration
-   Removed dead file `src/view/nodes.py`

## [1.0.0-alpha9] - 2024-2-4

-   Fixed `template` attribute with the `view` template renderer
-   Added the `context` decorator and the `Context` type
-   Added the `headers` parameter to functions on `TestingContext`
-   Modified some behavior of automatic route inputs
-   Fixed syntax errors in `view init`
-   Added `Route.middleware`
-   Routes with equivalent paths but different methods now return `405 Method Not Allowed` when accessed
-   Added `route` and `App.route`
-   Added docstrings to router functions
-   Added the `JSON` response class
-   Added the `custom` body translate strategy
-   Made `method` a keyword-only parameter in `path`
-   Added the `extract_path` utility
-   Added the `view build` command
-   Added `App.template`
-   Route errors now display the error message when `dev` is `True`
-   Changed exception rendering in route errors to use the `rich` renderer
-   Added `compile_type` and `TCValidator`
-   Added `markdown` and `App.markdown`
-   Added the `Error` class
-   Added the `error_class` parameter to both `new_app` and `App`
-   Added the `ERROR_CODES` constant
-   Completely rewrote docs
-   **Breaking Change:** The `body` parameter in `Response` is now required

## [1.0.0-alpha8] - 2024-1-21

-   Added optional dependencies for `databases` and `templates`
-   Added environment prefixes for database configuration
-   Added `templates` and `TemplatesConfig` to config
-   Added the `templates` function
-   Added support for `attrs` in type validation
-   Added documentation for caching
-   Added the `cache_rate` parameter to routers
-   Removed `psutil` and `plotext` as a global dependency
-   Added `fancy` optional dependencies
-   Fixed route inputs with synchronous routes
-   **Breaking Change:** Route inputs are now applied in the order of the decorator call as it appears in code

## [1.0.0-alpha7] - 2023-12-7

**Quick Patch Release**

-   Remerged new `view init` command.

## [1.0.0-alpha6] - 2023-11-30

-   Added `get_app`
-   Added documentation generation
-   Added database support (NOT FINISHED)
-   Removed `attempt_import` and `MissingLibraryError`
-   Added support for lists in type validation
-   Added support for implicit query parameters
-   Renamed `debug` to `enable_debug`
-   Added `debug`, `info`, `warning`, `error`, and `critical` logging functions
-   Added `InvalidRouteError`, `DuplicateRouteError`, `ViewInternalError`, and `ConfigurationError`
-   Renamed `EnvironmentError` to `BadEnvironmentError`
-   Added logging functions to `App`
-   Changed environment prefixes for configuration
-   Rewrote documentation
-   Added `patterns` loader
-   Added handling of relative paths in the configuration setting `loader_path`
-   Added exists validation to `loader_path`
-   Add path to `PATH` environment variable during loading
-   Upgraded `view init`

## [1.0.0-alpha5] - 2023-09-24

-   Added `app.query` and `app.body`
-   Patched warning with starting app from incorrect filename
-   Updated `__all__` for `routing.py`
-   Added `view.Response` and `view.HTML`
-   Fixed `__view_result__`
-   Added support for `__view_body__` and `__view_construct__`
-   Added support for Pydantic, `NamedTuple`, and dataclasses for type validation
-   Support for direct union types (i.e. `str | int`, `Union[str, int]`) on type validation
-   Added support for non async routes

## [1.0.0-alpha4] - 2023-09-10

-   Added type validation (without support for `__view_body__`)
-   Patched query strings on app testing
-   Added tests for query and body parameters
-   Patched body parameters
-   Documented type validation
-   Patched bodies with testing

## [1.0.0-alpha3] - 2023-09-9

-   Patched header responses
-   Added tests for headers
-   Updated repr for `Route`
-   Patched responses with three values
-   Documented responses and result protocol

## [1.0.0-alpha2] - 2023-09-9

-   Added `App.test()`
-   Added warning when filename does not match `app_path`
-   Added more tests
-   Upgrade CIBW to work on 3.11

## [1.0.0-alpha1] - 2023-08-17

Initial.
