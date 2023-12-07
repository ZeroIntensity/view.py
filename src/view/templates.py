from pathlib import Path
from typing import Any, Literal

import aiofiles

from .response import HTML

__all__ = ("template",)

_UseConfig = None

TemplateEngine = Literal["jinja"]


async def template(
    name: str | Path,
    directory: str | Path | None = _UseConfig,
    engine: TemplateEngine = "jinja",
    **parameters: Any,
) -> HTML:
    ...
