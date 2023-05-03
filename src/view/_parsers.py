import ujson

from .typing import ViewBody


def json_parser(data: str) -> ViewBody:
    return ujson.loads(data)
