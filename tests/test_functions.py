import os
from dataclasses import dataclass
from typing import Dict

from typing_extensions import Annotated

import pytest
from view import App, BadEnvironmentError, TypeValidationError, compile_type, env, get_app, new_app
from leaks import limit_leaks

@limit_leaks("1 MB")
def test_app_creation():
    app = new_app()
    assert isinstance(app, App)
    app.load()


@limit_leaks("1 MB")
def test_app_fetching():
    app = new_app()
    assert isinstance(get_app(), App)
    app.load()
    assert app is get_app()


def documentation_generation():
    app = new_app()

    @dataclass
    class Test:
        id: int

    @dataclass
    class Person:
        """A person."""

        first: Annotated[str, "Your first name."]
        last: Annotated[str, "Your last name."]
        parent: Test

    @app.get("/")
    @app.query("person", Person, doc="Your info.")
    @app.body("friend", Person, doc="Your friend's info.")
    @app.query("favorite_color", str, doc="Your favorite color.")
    @app.query("contacts", Dict[str, int], doc="Your phone contacts.")
    async def index(
        person: Person,
        friend: Person,
        favorite_color: str,
        contacts: Dict[str, int],
    ):
        """Homepage."""
        return "hello world"

    assert (
        app.docs()
        == """# Docs
## Types
### `Person`
| Key | Description | Type | Default |
| - | - | - | - |
| first | Your first name. | `string` | **Required** |
| last | Your last name. | `string` | **Required** |
| parent | No description provided. | `Test` | **Required** |
### `Test`
| Key | Description | Type | Default |
| - | - | - | - |
| id | No description provided. | `integer` | **Required** |
## Routes
### GET `/`
*Homepage.*
#### Query Parameters
| Name | Description | Type | Default |
| - | - | - | - |
| person | Your info. | `Person` | **Required** |
| favorite_color | Your favorite color. | `string` | **Required** |
| contacts | Your phone contacts. | `object<string, integer>` | **Required** |
#### Body Parameters
| Name | Description | Type | Default |
| - | - | - | - |
| friend | Your friend's info. | `Person` | **Required** |"""
    )


@pytest.mark.asyncio
@limit_leaks("1 MB")
async def test_public_typecode_interface():
    @dataclass
    class Test:
        a: str
        b: str

    tp = compile_type(Test)
    assert isinstance(tp.cast('{"a": "a", "b": "b"}'), Test)

    x = True

    if tp.check_type('{"a": "a", "b": "b"}'):
        x = False

    assert x
    if tp.is_compatible('{"a": "a", "b": "b"}'):
        x = False

    assert not x

    with pytest.raises(TypeValidationError):
        tp.cast("{}")


@pytest.mark.asyncio
async def test_environment_variables():
    with pytest.raises(BadEnvironmentError):
        env("_TEST")

    os.environ["_TEST"] = "1"

    assert env("_TEST") == "1"
    assert env("_TEST", tp=int) == 1
    os.environ["_TEST2"] = '{"hello": "world"}'
    
    test2 = env("_TEST2", tp=dict)
    assert isinstance(test2, dict)
    assert test2["hello"] == "world"

    os.environ["_TEST3"] = "false"
    assert env("_TEST3", tp=bool) is False

    
