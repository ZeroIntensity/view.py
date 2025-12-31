import pytest

from view.exceptions import InvalidType
from view.core.app import as_app, App


def test_as_app_invalid():
    with pytest.raises(InvalidType):
        as_app(object())  # type: ignore


def test_invalid_type_route():
    app = App()

    with pytest.raises(InvalidType):
        app.get(object())  # type: ignore

    with pytest.raises(InvalidType):
        app.get("/")(object())  # type: ignore
