# flake8: noqa
try:
    import _view
except ImportError as e:
    raise ImportError(
        "_view has not been built, did you forget to compile it?"
    ) from e

from . import _codec
from .__about__ import __license__, __version__
from .app import App, new_app
from .compiler import compile
from .config import AppConfig, Config, NetworkConfig, config
from .util import debug, run
