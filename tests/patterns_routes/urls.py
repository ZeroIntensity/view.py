from _routes import d, g, inputs, o, p, pa, pu, r

from view import path, query

PATTERNS = (
    path("/get", g),
    path("/post", p),
    path("/put", pu, method="put"),
    path("/patch", pa),
    path("/delete", d),
    path("/options", o),
    path("/any", r),
    path("/inputs", inputs, query("a", str))
)
