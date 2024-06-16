from typing import Any

from ._util import needs_dep

__all__ = "page",

try:
    from reactpy.core.types import VdomDict
    from reactpy.core.vdom import make_vdom_constructor

    _html = make_vdom_constructor("html")
    _body = make_vdom_constructor("body")

    def page(head: VdomDict, *body: VdomDict, lang: str = "en") -> VdomDict:  # type: ignore
        return _html({"lang": lang}, head, _body(*body))

except ImportError:
    VdomDict = dict[str, Any]

    def page(head: VdomDict, *body: VdomDict, lang: str = "en") -> VdomDict:
        needs_dep("reactpy")
