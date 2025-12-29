from typing import ParamSpec, Callable, Iterator, Protocol, runtime_checkable
from io import StringIO

from view.exceptions import InvalidType


__all__ = "SupportsJavaScript", "as_javascript_expression", "javascript_compiler"

P = ParamSpec("P")


@runtime_checkable
class SupportsJavaScript(Protocol):
    """
    Protocol for objects that want to allow use in `as_javascript_expression()`.
    """

    def as_javascript(self) -> str:
        """
        Convert this object into a single JavaScript expression.
        """
        ...


def as_javascript_expression(data: object) -> str:
    """
    Convert an object into a single JavaScript expression.
    """

    if isinstance(data, str):
        return repr(data)

    if isinstance(data, int):
        return str(data)

    if isinstance(data, bool):
        if data is True:
            return "true"
        else:
            assert data is False
            return "false"

    if isinstance(data, dict):
        result = StringIO()
        result.write("{")
        for key, value in data.items():
            key_expression = as_javascript_expression(key)
            value_expression = as_javascript_expression(value)
            result.write(f"{key_expression}: {value_expression},")
        result.write("}")
        return result.getvalue()

    if isinstance(data, SupportsJavaScript):
        result = data.as_javascript()
        if __debug__ and not isinstance(result, str):
            raise InvalidType(str, result)

    raise TypeError(f"Don't know how to convert {data!r} to a JavaScript expression")


def javascript_compiler(function: Callable[P, Iterator[str]]) -> Callable[P, str]:
    """
    Decorator that converts a function yielding lines of JavaScript code into
    a function that returns the entire source code.
    """

    def decorator(*args: P.args, **kwargs: P.kwargs) -> str:
        buffer = StringIO()

        for line in function(*args, **kwargs):
            if __debug__ and not isinstance(line, str):
                raise InvalidType(str, line)
            buffer.write(f"{line};\n")

        return buffer.getvalue()

    return decorator
