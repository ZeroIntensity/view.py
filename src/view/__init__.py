try:
    import _view
except ImportError as e:
    raise ImportError(
        "_view extension has not been built, did you forget to compile it?"
    ) from e

from .__about__ import __license__, __version__
