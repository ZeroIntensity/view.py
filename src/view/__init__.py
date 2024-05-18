# flake8: noqa
"""
view.py - The Batteries-Detachable Web Framework

Docs: https://view.zintensity.dev
GitHub: https://github.com/zerointensity/view.py
"""
try:
    import _view
except ModuleNotFoundError as e:
    raise ImportError(
        "_view has not been built, did you forget to compile it?"
    ) from e

# these are re-exports
from _view import Context, InvalidStatusError, WebSocketHandshakeError

from . import _codec
from .__about__ import *
from .app import *
from .build import *
from .exceptions import *
from .logging import *
from .patterns import *
from .response import *
from .routing import *
from .templates import *
from .typecodes import *
from .util import *
