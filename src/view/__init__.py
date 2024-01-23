# flake8: noqa
"""
view.py - The Batteries-Detachable Web Framework

Docs: https://view.zintensity.dev
GitHub: https://github.com/zerointensity/view.py
"""
try:
    import _view
except ImportError as e:
    raise ImportError("_view has not been built, did you forget to compile it?") from e

from _view import Context  # re-export

from . import _codec
from .__about__ import *
from .app import *
from .components import *
from .exceptions import *
from .logging import *
from .patterns import *
from .response import *
from .routing import *
from .templates import *
from .util import *
