from _routes import d, g, o, p, pa, pu

from view import path

PATTERNS = (
    path("/get", g),
    path("/post", p),
    path("/put", pu, method="put"),
    path("/patch", pa),
    path("/delete", d),
    path("/options", o),
)
