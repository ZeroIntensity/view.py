from dataclasses import dataclass
from typing import Dict

from typing_extensions import Annotated
from ward import test

from view import App, get_app, new_app


@test("app creation")
def _():
    app = new_app()
    assert isinstance(app, App)
    app.load()


@test("app fetching")
def _():
    app = new_app()
    assert isinstance(get_app(), App)
    app.load()
    assert app is get_app()


@test("documentation generation")
def _():
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
