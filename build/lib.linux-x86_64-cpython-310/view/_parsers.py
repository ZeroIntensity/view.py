from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import parse_qs

import ujson

from .typing import ViewBody

if TYPE_CHECKING:
    from .app import App


def query_parser(data: str) -> ViewBody:
    parsed = parse_qs(data)
    final = {}
    for k, v in parsed.items():
        if len(v) == 1:
            final[k] = v[0]
        else:
            final[k] = v

    return final


def supply_parsers(app: App):
    app._supply_parsers(query_parser, ujson.loads)
