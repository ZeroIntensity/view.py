from typing import AsyncIterator, Callable, Iterator
import pytest
from view.dom.primitives import ALL_PRIMITIVES, html, div, p
from view.dom.core import HTMLNode, html_response, html_context
import inspect

from view.app import App
from view.testing import AppTestClient


def html_function(
    node: Callable[..., HTMLNode], *, has_body: bool
) -> Iterator[HTMLNode]:
    with html(lang="en"):
        with div(data={"foo": "bar"}):
            if has_body:
                yield node("gotcha", data={"silly": "a"})
            else:
                yield node(data={"silly": "a"})


@pytest.mark.parametrize("dom_node", ALL_PRIMITIVES)
def test_dom_primitives(dom_node: Callable[..., HTMLNode]):
    with html_context() as parent:
        parameters = inspect.signature(dom_node).parameters
        has_body = parameters.get("child_text") is not None
        has_required = False
        for parameter in parameters.values():
            if parameter.name == "global_attributes":
                continue

            if parameter.default is inspect.Signature.empty:
                has_required = True

        if not has_required:
            for _ in html_function(dom_node, has_body=has_body):
                pass
        else:
            with pytest.raises(TypeError):
                for _ in html_function(dom_node, has_body=has_body):
                    pass

            return

        iterator = parent.as_html_stream()
        assert "<html" == next(iterator)
        assert 'lang="en"' in next(iterator)
        assert ">" in next(iterator)
        assert "<div" in next(iterator)
        assert 'data-foo="bar"' in next(iterator)
        assert ">" in next(iterator)
        real_node_name = dom_node.__name__.removesuffix("_")
        assert f"<{real_node_name}" in next(iterator)
        assert 'data-silly="a"' in next(iterator)
        assert ">" in next(iterator)
        if has_body:
            assert f"gotcha" in next(iterator)
        assert f"</{real_node_name}>" in next(iterator)
        assert f"</div>" in next(iterator)
        assert f"</html>" == next(iterator)
        with pytest.raises(StopIteration):
            next(iterator)


@pytest.mark.asyncio
async def test_html_response():
    app = App()

    @app.get("/")
    @html_response
    async def index() -> AsyncIterator[HTMLNode | int]:
        yield 201
        with html():
            with div():
                yield p("test")

    client = AppTestClient(app)
    response = await client.get("/")
    assert response.status_code == 201
    body = (await response.body()).decode("utf-8")
    formatted = body.replace(" ", "").replace("\n", "")
    assert formatted == "<!DOCTYPEhtml><html><div><p>test</p></div></html>"
