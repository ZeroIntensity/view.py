from __future__ import annotations

import inspect
from pathlib import Path
from types import FrameType as Frame
from typing import Any, Type

import aiofiles

from .app import get_app
from .config import TemplatesConfig
from .exceptions import BadEnvironmentError
from .response import HTML
from .typing import TemplateEngine

_ConfigSpecified = None
_DEFAULT_CONF = TemplatesConfig()

__all__ = ("template",)


class _CurrentFrame:  # sentinel
    ...


_CurrentFrameType = Type[_CurrentFrame]


async def template(
    name: str | Path,
    directory: str | Path | None = _ConfigSpecified,
    engine: TemplateEngine | None = _ConfigSpecified,
    frame: Frame | None | _CurrentFrameType = _CurrentFrame,
    **parameters: Any,
) -> HTML:
    try:
        conf = get_app().config.templates
    except BadEnvironmentError:
        conf = _DEFAULT_CONF

    directory = directory or conf.directory
    engine = engine or conf.engine

    if isinstance(name, str):
        if not name.endswith(".html"):
            name += ".html"

        name = Path(name)

    path = directory / name
    params: dict[str, Any] = {}

    if frame:
        if frame is _CurrentFrame:
            frame = inspect.currentframe()
            assert frame, "failed to get frame"

        assert isinstance(frame, Frame)

        if conf.globals:
            params.update(frame.f_globals)

        if conf.locals:
            params.update(frame.f_locals)

    params.update(parameters)

    async with aiofiles.open(path) as f:
        text = await f.read()

    return HTML("")
