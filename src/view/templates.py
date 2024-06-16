"""
view.py templating APIs

This module contains all APIs related to rendering HTML through a template engine. As of this docstring being written, view.py supports the following engines:
    - view.py's own template engine
    - Jinja2
    - Django's template engine
    - Mako
    - Chameleon
"""
from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path
from types import FrameType as Frame
from types import ModuleType
from typing import TYPE_CHECKING, Any, Iterator, Type

import aiofiles

from ._util import needs_dep
from .config import TemplatesConfig
from .exceptions import BadEnvironmentError, InvalidTemplateError
from .response import HTML
from .typing import TemplateEngine

if TYPE_CHECKING:
    from bs4 import Tag

    from .app import App

_ConfigSpecified = None
_DEFAULT_CONF = TemplatesConfig()

__all__ = ("template", "render", "markdown")


class _CurrentFrame:  # sentinel
    pass


_CurrentFrameType = Type[_CurrentFrame]

_DJANGO_HOOK = ModuleType("_view_django")
sys.modules["_view_django"] = _DJANGO_HOOK

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_view_django")


class _ViewRenderer:
    def __init__(self, parameters: dict[str, Any]):
        self.parameters = parameters
        self._last_if: bool | None = None

    async def _render_children(
        self, view: Tag, result: list[Any], *, defer: bool = False
    ) -> None:
        from bs4 import Tag

        for child in view.children:
            if isinstance(child, Tag):
                if child.name == "view":
                    ele = await self._tag(child, defer=defer)
                    if ele:
                        result.append(ele)
            else:
                result.append(child)

    async def _tag(
        self,
        view: Tag,
        *,
        defer: bool = False,
    ) -> Tag | str | None:
        from bs4 import BeautifulSoup

        if not view.attrs:
            raise InvalidTemplateError(
                "<view> tags must have at least one attribute"
            )

        iterator_obj: Iterator[Any] | None = None
        iterator_name: str | None = None

        def _iter_render(itera: str, item: str) -> None:
            if not itera:
                raise InvalidTemplateError('"iter" attribute cannot be empty')

            if not item:
                raise InvalidTemplateError('"item" attribute cannot be empty')

            nonlocal iterator_obj
            iterator_obj = iter(eval(itera, self.parameters))
            nonlocal iterator_name
            iterator_name = item

        result: list[str | Tag] = []

        for key, value in view.attrs.items():
            if key == "ref":
                func = repr if "repr" in view.attrs else str
                ref: str = func(eval(value, self.parameters))
                if "nosanitize" in view.attrs:
                    result.append(BeautifulSoup(ref, "html.parser"))
                else:
                    result.append(ref)
            elif key in {"nosanitize", "repr"}:
                if "ref" not in view.attrs:
                    raise InvalidTemplateError(
                        "f{key} can only be used with a ref attribute in <view> tag"
                    )
            elif key == "template":
                html = await template(value)
                body = html._custom(html.body)
                result.append(body)
            elif key == "if":
                self._last_if = bool(eval(value, self.parameters))
                if not self._last_if:
                    if not defer:
                        view.replace_with("")
                    return None
            elif (key in {"else", "elif"}) and (self._last_if is None):
                raise InvalidTemplateError(
                    f'{key} can only be used if an "if" attribute was used prior'
                )  # noqa
            elif key == "else":
                if self._last_if is True:
                    if not defer:
                        view.replace_with("")
                    return None
            elif key == "elif":
                if self._last_if is False:
                    self._last_if = bool(eval(value, self.parameters))
                    if not self._last_if:
                        if not defer:
                            view.replace_with("")
                        return None
                else:
                    if not defer:
                        view.replace_with("")
                    return None

            elif key == "iter":
                item = view.attrs.get("item")
                if not item:
                    raise InvalidTemplateError(
                        '<view> tags with an "iter" attribute must have an "item" attribute'
                    )  # noqa

                _iter_render(value, item)
            elif key == "item":
                iter_name = view.attrs.get("iter")
                if not iter_name:
                    raise InvalidTemplateError(
                        '<view> tags with an "item" attribute must have an "iter" attribute'
                    )  # noqa

                _iter_render(iter_name, value)
            else:
                raise InvalidTemplateError(
                    f"unknown attribute {key!r} in <view> tag"
                )

        if iterator_obj:
            assert iterator_name, "iterator_name is None (this is a bug!)"

            for i in iterator_obj:  # type: ignore
                self.parameters[iterator_name] = i
                await self._render_children(view, result, defer=True)

            iterator_obj = None
        else:
            await self._render_children(view, result)

        return (
            view.replace_with(*result)
            if not defer
            else "\n".join([str(i) for i in result])
        )

    async def render(self, content: str) -> str:
        try:
            from bs4 import BeautifulSoup, Tag
        except ModuleNotFoundError as e:
            needs_dep("beautifulsoup4", e, "templates")

        soup = BeautifulSoup(content, features="html.parser")

        for view in soup.find_all("view"):
            assert isinstance(
                view, Tag
            ), "found non-tag somehow (this is a bug!)"
            await self._tag(view)

        return str(soup)


async def render(
    source: str,
    engine: TemplateEngine = "view",
    parameters: dict[str, Any] | None | _CurrentFrameType = _CurrentFrame,
    *,
    app: App | None = None,
) -> str:
    """
    Render a template from the source instead of a filename.
    Generally should be used internally, but is considered stable.

    This function does not require that an app has been created, but will attempt to get an app with `get_app()` regardless.
    If `get_app()` fails, template engine instances are not stored.
    
    Args:
        source: Source code to pass to the template engine.
        engine: Template engine to use. Unlike `template()`, this does not try and load the default template engine from the config.
        parameters: Variables to pass to the template engine for use in templates. By default, this will attempt to steal locals from the callers frame.
        app: App to store engines on. If `None`, will attempt to call `get_app()`.

    Example:
        ```py
        import aiofiles
        from view import render


        async def main():
            async with aiofiles.open("template.html") as f:
                html = await render(await f.read(), engine="jinja")
        ```
    """
    from .app import get_app

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

    try:
        templaters = (app or get_app()).templaters
    except BadEnvironmentError:
        templaters = {}

    if engine == "view":
        view = _ViewRenderer(parameters or {})  # type: ignore
        return await view.render(source)
    elif engine == "jinja":
        try:
            from jinja2 import Environment
        except ModuleNotFoundError as e:
            needs_dep("jinja2", e, "templates")

        env: Environment | None = templaters.get("jinja")
        if not env:
            templaters["jinja"] = Environment()
            env = templaters["jinja"]
            env.is_async = True

        return await env.from_string(source).render_async(**parameters)  # type: ignore
    elif engine == "mako":
        try:
            from mako.template import Template
        except ModuleNotFoundError as e:
            needs_dep("mako", e, "templates")

        return Template(source).render_unicode(**parameters)  # type: ignore
    elif engine == "chameleon":
        try:
            from chameleon.zpt.template import PageTemplate
        except ModuleNotFoundError as e:
            needs_dep("chameleon", e, "templates")

        return PageTemplate(source)(**parameters)  # type: ignore
    elif engine == "django":
        try:
            from django import setup
            from django.conf import settings
            from django.template import Context, Template
        except ModuleNotFoundError as e:
            needs_dep("django", e, "templates")

        TEMPLATES = [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": False,
                "OPTIONS": {},
            }
        ]
        settings.configure(TEMPLATES=TEMPLATES)
        setup()

        return Template(source).render(Context(parameters))
    else:
        raise InvalidTemplateError(
            f"{engine!r} is not a supported template engine"
        )


async def template(
    name: str | Path,
    directory: str | Path | None = _ConfigSpecified,
    engine: TemplateEngine | None = _ConfigSpecified,
    frame: Frame | None | _CurrentFrameType = _CurrentFrame,
    app: App | None = None,
    **parameters: Any,
) -> HTML:
    """
    Render a template with the specified engine.

    Args:
        name: A string, which is appended the `.html` suffix (if it doesn't have it already), or a `Path` object, representing a file containing an HTML template.
        directory: Directory to search for templates. If this is `None`, the directory specified in the configuration is used.
        engine: Template engine to choose. If this is `None`, the default engine specified in the configuration is used.
        frame: Frame to steal locals from for parameters. This will use the callers frame by default. If this is `None`, then no locals are sent to the template engine.
        app: App instance to store template engine instances on. If this is `None`, `get_app` is called.
        parameters: Extra values to send to the template engine as variables.

    Example:
        ```py
        from view import get, template

        @get("/")
        async def index():
            return await template("test")
        ```
    """
    from .app import get_app

    try:
        conf = app.config.templates if app else get_app().config.templates
    except BadEnvironmentError:
        conf = _DEFAULT_CONF

    directory = Path(directory or conf.directory)
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
        source = await f.read()

    return HTML(await render(source, engine, params, app=app))


async def markdown(
    name: str | Path,
    *,
    directory: str | Path | None = _ConfigSpecified,
    app: App | None = None,
) -> HTML:
    """
    Convert a markdown file into HTML.

    Args:
        name: Equivalent to `name` in `template()`, with the exception of using the `.md` suffix instead of `.html`.
        directory: Equivalent to `directory` in `template()`.
        app: Equivalent to `app` in `template()`.

    Raises:
        NeedsDependencyError: `markdown` module is not installed.
    """
    from .app import get_app

    try:
        from markdown import markdown as md_to_html
    except ModuleNotFoundError as e:
        needs_dep("markdown", e, "templates")

    try:
        conf = app.config.templates if app else get_app().config.templates
    except BadEnvironmentError:
        conf = _DEFAULT_CONF

    directory = Path(directory or conf.directory)

    if isinstance(name, str):
        if not name.endswith(".md"):
            name += ".md"

        name = Path(name)

    path = directory / name
    async with aiofiles.open(path) as f:
        source = await f.read()

    return HTML(f"<!DOCTYPE html><html>{md_to_html(source)}</html>")
