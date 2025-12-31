import pytest
from view.core.app import App, as_app
from view.exceptions import InvalidType


def test_as_app_invalid():
    with pytest.raises(InvalidType):
        as_app(object())  # type: ignore


def test_invalid_type_route():
    app = App()

    with pytest.raises(InvalidType):
        app.get(object())  # type: ignore

    with pytest.raises(InvalidType):
        app.get("/")(object())  # type: ignore
