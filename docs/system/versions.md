# Versioning

## Version Guarantees

View follows [semantic versioning](https://semver.org/). For more information, see their page. In short:

- `MAJOR` versions are **not backwards compatible**.
- `MINOR` versions are *mostly* backwards compatible, with the exception of small breaking changes. For information about breaking changes, see [the changelog](https://github.com/ZeroIntensity/view.py/blob/master/CHANGELOG.md).
- `PATCH` versions are always backwards compatible, and generally only add bugfixes.

For example, code built on `1.0.0` would be incompatible with `2.0.0`, but `2.1.0` is compatible with code built in `2.0.0`.
