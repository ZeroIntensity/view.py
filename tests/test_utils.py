import pytest
from view.utils import reraise


def test_simple_reraise():
    with pytest.raises(RuntimeError) as error:
        with reraise(RuntimeError, TypeError):
            raise TypeError("hello")

    assert str(error.value) == ""


def test_reraise_no_match():

    with pytest.raises(ValueError) as error:
        with reraise(RuntimeError, TypeError):
            raise ValueError("silly")

    assert str(error.value) == "silly"


def test_reraise_all_exceptions():

    with pytest.raises(RuntimeError) as error:
        with reraise(RuntimeError):
            raise ZeroDivisionError("123")

    assert str(error.value) == ""


def test_reraise_exception_value():

    with pytest.raises(RuntimeError) as error:
        with reraise(RuntimeError("something")):
            raise ZeroDivisionError("456")

    assert str(error.value) == "something"


def test_reraise_multiple():

    with pytest.raises(RuntimeError):
        with reraise(RuntimeError, TypeError, ValueError):
            raise ValueError

    with pytest.raises(RuntimeError):
        with reraise(RuntimeError, TypeError, ValueError):
            raise TypeError


def test_do_not_reraise_base_exceptions():

    with pytest.raises(KeyboardInterrupt):
        with reraise(RuntimeError):
            raise KeyboardInterrupt


def test_simple_reraise_as_decorator():
    @reraise(RuntimeError, TypeError)
    def runtime_from_type() -> None:
        raise TypeError("silly")

    with pytest.raises(RuntimeError):
        runtime_from_type()


def test_reraise_unexpected_as_decorator():

    @reraise(RuntimeError, TypeError)
    def runtime_from_type_but_value() -> None:
        raise ValueError("haha")

    with pytest.raises(ValueError):
        runtime_from_type_but_value()


def test_reraise_all_exceptions_as_decorator():

    @reraise(RuntimeError)
    def runtime_from_all() -> None:
        raise ZeroDivisionError("anything")

    with pytest.raises(RuntimeError):
        runtime_from_all()


def test_reraise_exception_instance_as_decorator():

    @reraise(RuntimeError("test"))
    def runtime_value_from_all() -> None:
        raise ZeroDivisionError("anything")

    with pytest.raises(RuntimeError) as error:
        runtime_value_from_all()

    assert str(error.value) == "test"


def test_multi_reraise_as_decorator():

    @reraise(RuntimeError, TypeError, ValueError)
    def runtime_from_type_or_value(exception: BaseException) -> None:
        raise exception

    with pytest.raises(RuntimeError):
        runtime_from_type_or_value(ValueError("foo"))

    with pytest.raises(RuntimeError):
        runtime_from_type_or_value(TypeError("bar"))

    with pytest.raises(ZeroDivisionError):
        runtime_from_type_or_value(ZeroDivisionError())


def test_do_not_reraise_base_exceptions_as_decorator():
    @reraise(RuntimeError)
    def runtime_from_all_but_interrupt() -> None:
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        runtime_from_all_but_interrupt()
