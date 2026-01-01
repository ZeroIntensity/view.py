import pytest
from view.core.app import App, as_app
from view.exceptions import InvalidTypeError
from view.core.multi_map import HasMultipleValuesError, MultiMap


def test_as_app_invalid():
    with pytest.raises(InvalidTypeError):
        as_app(object())  # type: ignore


def test_invalid_type_route():
    app = App()

    with pytest.raises(InvalidTypeError):
        app.get(object())  # type: ignore

    with pytest.raises(InvalidTypeError):
        app.get("/")(object())  # type: ignore


def test_empty_multi_map():
    multi_map = MultiMap()
    assert multi_map == {}

    with pytest.raises(KeyError):
        multi_map["a"]

    with pytest.raises(KeyError):
        multi_map[object()]

    with pytest.raises(KeyError):
        multi_map[None]

    assert len(multi_map) == 0
    assert multi_map.as_sequence() == []

    called = False
    for _ in multi_map.keys():
        called = True

    assert called is False

    for _ in multi_map.values():
        called = True

    assert called is False

    for _ in multi_map.items():
        called = True

    assert called is False

    for _ in multi_map:
        called = True

    assert called is False


def test_multi_map_no_duplicates():
    data = [('a', 1), ('b', 2), ('c', 3)]
    multi_map = MultiMap(data)

    assert multi_map == {"a": 1, "b": 2, "c": 3}
    assert len(multi_map) == 3
    assert multi_map.as_sequence() == data

    for key, value in data:
        assert key in multi_map
        assert multi_map[key] == value
        assert multi_map.get_many(key) == [value]
        assert multi_map.get(key) == value
        assert multi_map.get_exactly_one(key) == value
        assert key in multi_map.keys()
        assert value in multi_map.values()

    called = 0
    for key in multi_map:
        called += 1
        assert key in ("a", "b", "c")

    assert called == 3



def test_multi_map_with_duplicates():
    data = [('a', 1), ('a', 2), ('a', 3), ('b', 4)]
    multi_map = MultiMap(data)
    assert len(multi_map) == 2
    assert multi_map.as_sequence() == data

    assert multi_map == {"a": 1, "b": 4}
    assert multi_map["a"] == 1
    assert multi_map.get_many("a") == [1, 2, 3]

    assert "a" in multi_map
    assert "b" in multi_map
    assert list(multi_map.keys()) == ['a', 'b']
    assert list(multi_map.values()) == [1, 4]
    assert list(multi_map.items()) == [('a', 1), ('b', 4)]
    assert list(multi_map.many_values()) == [[1, 2, 3], [4]]
    assert list(multi_map.many_items()) == [('a', [1, 2, 3]), ('b', [4])]

    with pytest.raises(HasMultipleValuesError):
        multi_map.get_exactly_one('a')

    assert multi_map.get_exactly_one("b") == 4

    called = 0
    for key in multi_map:
        called += 1
        assert key in ("a", "b")

    assert called == 2


def test_multi_map_with_new_value():
    data = [('a', 1), ('b', 2), ('b', 3)]
    multi_map = MultiMap(data)
    assert len(multi_map) == 2

    new_map = multi_map.with_new_value('b', 4)
    assert len(new_map) == 2
    assert "b" in new_map
    assert multi_map != new_map
    assert new_map.get_many("b") == [2, 3, 4]

    new_map = new_map.with_new_value("c", 4)
    assert len(new_map) == 3
    assert "c" in new_map
    assert new_map != multi_map
    assert new_map["c"] == 4
    assert new_map.get_exactly_one("c") == 4
    assert new_map.get_many("b") == [2, 3, 4]
