# flake8: noqa
"""
view.py - A modern web framework

Docs: https://view.zintensity.dev
GitHub: https://github.com/zerointensity/view.py
"""
try:
    import _view
except ImportError as e:
    raise ImportError(
        "_view has not been built, did you forget to compile it?"
    ) from e

from . import _codec
from .__about__ import __license__, __version__
from .app import *
from .components import *
from .exceptions import *
from .response import *
from .routing import *
from .util import *
