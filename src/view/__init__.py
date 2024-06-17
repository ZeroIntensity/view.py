# flake8: noqa
"""
view.py - The Batteries-Detachable Web Framework

Docs: https://view.zintensity.dev
GitHub: https://github.com/zerointensity/view.py
Support: https://github.com/sponsors/ZeroIntensity

MIT License

Copyright (c) 2024 ZeroIntensity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
try:
    import _view
except ModuleNotFoundError as e:
    raise ImportError("the _view extension module is missing! view.py cannot be used with pure python") from e

# these are re-exports
from _view import Context, HeaderDict, InvalidStatusError

from .__about__ import *
from .app import *
from .build import *
from .default_page import *
from .exceptions import *
from .integrations import *
from .logging import *
from .patterns import *
from .response import *
from .routing import *
from .templates import *
from .typecodes import *
from .util import *
from .ws import *
