from __future__ import annotations

import os
import runpy
import warnings
from typing import TYPE_CHECKING

from ._logging import Internal
from .routing import Route

if TYPE_CHECKING:
    from .app import ViewApp


def _finalize(routes: list[Route], app: ViewApp):
    for route in routes:
        print(route)


def load_fs(app: ViewApp, target_dir: str):
    Internal.info("loading using filesystem")
    Internal.debug(f"loading {app}")

    routes: list[Route] = []

    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.startswith("_"):
                continue

            path = os.path.join(root, f)
            Internal.info(f"loading: {path}")
            mod = runpy.run_path(path)
            route: Route | None = None

            for i in mod.values():
                if isinstance(i, Route):
                    if route:
                        warnings.warn("set route twice!")
                    route = i

            if not route:
                raise ValueError(f"{path} has no set route")

            if route.path:
                warnings.warn(
                    "path was passed when filesystem loading is enabled"
                )
            else:
                route.path = path.rsplit(".", maxsplit=1)[0]

            routes.append(route)

    _finalize(routes, app)


def load_simple(app: ViewApp, target_dir: str):
    Internal.info("loading using simple strategy")
    routes: list[Route] = []

    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.startswith("_"):
                continue

            path = os.path.join(root, f)
            Internal.info(f"loading: {path}")
            mod = runpy.run_path(path)
            mini_routes: list[Route] = []

            for i in mod.values():
                if isinstance(i, Route):
                    mini_routes.append(i)

            for route in mini_routes:
                if not route.path:
                    raise ValueError(
                        "omitting path is only supported"
                        " on filesystem loading",
                    )

                routes.append(route)

    _finalize(routes, app)
