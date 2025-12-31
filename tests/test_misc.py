import pytest
from view.core.app import App, as_app
from view.exceptions import InvalidTypeError


def test_as_app_invalid():
    with pytest.raises(InvalidTypeError):
        as_app(object())  # type: ignore


def test_invalid_type_route():
    app = App()

    with pytest.raises(InvalidTypeError):
        app.get(object())  # type: ignore

    with pytest.raises(InvalidTypeError):
        app.get("/")(object())  # type: ignore
