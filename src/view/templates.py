from __future__ import annotations

import inspect
from pathlib import Path
from types import FrameType as Frame
from typing import TYPE_CHECKING, Any, Type

import aiofiles
import aiohttp
from yarl import URL

from ._util import needs_dep
from .app import get_app
from .config import TemplatesConfig
from .exceptions import BadEnvironmentError, InvalidTemplateError
from .response import HTML
from .typing import TemplateEngine

if TYPE_CHECKING:
    from bs4 import Tag

_ConfigSpecified = None
_DEFAULT_CONF = TemplatesConfig()

__all__ = ("template",)


class _CurrentFrame:  # sentinel
    ...


_CurrentFrameType = Type[_CurrentFrame]


def _view_cond(view: Tag, parameters: dict[str, Any]):
    from bs4 import Tag

    length = len(list(view.children))
    if not length:
        raise InvalidTemplateError(
            "<view condition> must have 2 or more children",
        )

    for i in view.children:
        if not isinstance(i, Tag) or (i.name != "view"):
            raise InvalidTemplateError(
                "children of a <view condition> must be view tags"
            )

    for i in view.children:
        if_attr = view.attrs.get("if")
        else_attr = view.attrs.get("else")


async def _view_tag(
    view: Tag,
    parameters: dict[str, Any],
) -> None:
    if not view.attrs:
        raise InvalidTemplateError("<view> tags must have attributes")

    result = []

    for key, value in view.attrs.items():
        if key == "ref":
            result.append(str(eval(value, parameters)))
        elif key == "template":
            result.append(await template(value))
        elif key == "page":
            app = get_app()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    URL()
                    .with_host(str(app.config.server.host))
                    .with_scheme("http")
                    .with_port(app.config.server.port)
                    .with_path(value)
                ) as res:
                    result.append(await res.text())
        elif key == "condition":
            _view_cond(i, parameters)
        elif key in {"if", "else"}:
            raise InvalidTemplateError(
                f"you must be in a <view condition> to use {key}"
            )

    view.replace_with("\n".join(result))


async def _view_render(content: str, parameters: dict[str, Any]) -> str:
    try:
        from bs4 import BeautifulSoup, Tag
    except ModuleNotFoundError as e:
        needs_dep("beautifulsoup4", e, "templates")

    soup = BeautifulSoup(content, features="html.parser")

    for view in soup.find_all("view"):
        assert isinstance(view, Tag), "found non-tag somehow (this is a bug!)"
        await _view_tag(view, parameters)

    return str(soup)


async def render(
    content: str,
    engine: TemplateEngine = "view",
    parameters: dict[str, Any] | None | _CurrentFrameType = _CurrentFrame,
) -> str:
    if parameters is _CurrentFrame:
        parameters = {}
        frame = inspect.currentframe()
        assert frame, "failed to get frame"
        while frame.f_code.co_filename == __file__:
            frame = frame.f_back
            assert frame, "frame has no f_back"

        assert isinstance(frame, Frame)

        parameters.update(frame.f_globals)
        parameters.update(frame.f_locals)

    return await _view_render(content, parameters or {})  # type: ignore


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
            while frame.f_code.co_filename == __file__:
                frame = frame.f_back
                assert frame, "frame has no f_back"

        assert isinstance(frame, Frame)

        if conf.globals:
            params.update(frame.f_globals)

        if conf.locals:
            params.update(frame.f_locals)

    params.update(parameters)

    async with aiofiles.open(path) as f:
        text = await f.read()

    return HTML("")
