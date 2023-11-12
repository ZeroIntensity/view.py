# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- Added `get_app`
- Added documentation generation
- Added support for lists in type validation
- Added support for implicit query parameters
- Renamed `debug` to `enable_debug`
- Added `debug`, `info`, `warning`, `error`, and `critical` logging functions
- Added `InvalidRouteError`, `DuplicateRouteError`, `ViewInternalError`, and `ConfigurationError`
- Renamed `EnvironmentError` to `BadEnvironmentError`

## [1.0.0-alpha5] - 2023-09-24

- Added `app.query` and `app.body`
- Patched warning with starting app from incorrect filename
- Updated `__all__` for `routing.py`
- Added `view.Response` and `view.HTML`
- Fixed `__view_result__`
- Added support for `__view_body__` and `__view_construct__`
- Added support for Pydantic, `NamedTuple`, and dataclasses for type validation
- Support for direct union types (i.e. `str | int`, `Union[str, int]`) on type validation
- Added support for non async routes

## [1.0.0-alpha4] - 2023-09-10
- Added type validation (without support for `__view_body__`)
- Patched query strings on app testing
- Added tests for query and body parameters
- Patched body parameters
- Documented type validation
- Patched bodies with testing

## [1.0.0-alpha3] - 2023-09-9
- Patched header responses
- Added tests for headers
- Updated repr for `Route`
- Patched responses with three values
- Documented responses and result protocol

## [1.0.0-alpha2] - 2023-09-9

- Added `App.test()`
- Added warning when filename does not match `app_path`
- Added more tests
- Upgrade CIBW to work on 3.11

## [1.0.0-alpha1] - 2023-08-17

Initial.
