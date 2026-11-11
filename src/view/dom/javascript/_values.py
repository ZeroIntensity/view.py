"""Typed JavaScript expressions and values used by the recording compiler."""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping, Sequence
from typing import (
    TYPE_CHECKING,
    Generic,
    NoReturn,
    Protocol,
    TypeAlias,
    TypeVar,
    Union,
    runtime_checkable,
)

if TYPE_CHECKING:
    from ._compiler import CompileContext

T_co = TypeVar("T_co", covariant=True)
H = TypeVar("H", bound="JavaScriptHandle[object]")
R_co = TypeVar("R_co", bound="JavaScriptHandle[object]", covariant=True)


@runtime_checkable
class SupportsJavaScript(Protocol):
    """An object that supplies a trusted JavaScript expression."""

    def as_javascript(self) -> str: ...


JavaScriptValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | SupportsJavaScript
    | Sequence["JavaScriptValue"]
    | Mapping[str, "JavaScriptValue"]
)


def as_javascript_expression(data: JavaScriptValue) -> str:
    """Serialize values, including nested collections, without Python syntax.

    Strings are also safe inside HTML script elements. Custom expressions
    supplied through SupportsJavaScript are trusted source code.
    """
    if data is None:
        return "null"
    if isinstance(data, bool):
        return "true" if data else "false"
    if isinstance(data, str):
        return (
            json.dumps(data, ensure_ascii=True)
            .replace("<", r"\u003c")
            .replace(">", r"\u003e")
            .replace("&", r"\u0026")
        )
    if isinstance(data, int):
        if abs(data) > 2**53 - 1:
            raise ValueError(
                "Integer is outside JavaScript's safe number range"
            )
        return str(data)
    if isinstance(data, float):
        if math.isnan(data):
            return "NaN"
        if math.isinf(data):
            return "Infinity" if data > 0 else "(-Infinity)"
        return repr(data)
    if isinstance(data, SupportsJavaScript):
        result = data.as_javascript()
        if not isinstance(result, str):
            raise TypeError("as_javascript() must return a string")
        return result
    if isinstance(data, Mapping):
        entries: list[str] = []
        for key, value in data.items():
            if not isinstance(key, str):
                raise TypeError("JavaScript object keys must be strings")
            # Computed keys also treat '__proto__' as an ordinary own property.
            entries.append(
                f"[{as_javascript_expression(key)}]: "
                f"{as_javascript_expression(value)}"
            )
        return "{" + ", ".join(entries) + "}"
    if isinstance(data, Sequence) and not isinstance(data, (bytes, bytearray)):
        return "[" + ", ".join(map(as_javascript_expression, data)) + "]"
    raise TypeError(f"Cannot convert {type(data).__name__} to JavaScript")


class JavaScriptHandle(Generic[T_co]):
    """A typed expression in one CompileContext, never a Python value.

    Use explicit get/set/call_method operations for APIs without typed wrappers.
    Property names passed to those methods are JavaScript names, verbatim.
    """

    def __init__(self, context: CompileContext, expression: str) -> None:
        self._context = context
        self._expression = expression
        self._scope = tuple(context._scopes)
        self._writable = False

    def _copy(self: H, expression: str) -> H:
        return type(self)(self._context, expression)

    def as_javascript(self) -> str:
        self._context._validate(self)
        return self._expression

    def __bool__(self) -> NoReturn:
        raise TypeError(
            "JavaScript values cannot control Python flow; use "
            "ctx.condition(value).if_true()/if_false()/while_true(). "
            "Use & and | instead of Python 'and' and 'or'."
        )

    def __iter__(self) -> NoReturn:
        raise TypeError("Use ctx.for_of() to iterate over JavaScript values")

    def __str__(self) -> NoReturn:
        raise TypeError(
            "Use as_javascript() to explicitly render an expression"
        )

    def _compare(
        self, operator: str, other: JavaScriptValue
    ) -> JavaScriptBoolean:
        ctx = self._context
        return JavaScriptBoolean(
            ctx, f"({ctx._render(self)} {operator} {ctx._render(other)})"
        )

    # Python requires bool here, but comparisons build JavaScript expressions.
    # Keep the exception confined to these two special methods.
    def __eq__(self, other: object) -> JavaScriptBoolean:  # type: ignore[override]
        return self._compare("===", self._context._checked_value(other))

    def __ne__(self, other: object) -> JavaScriptBoolean:  # type: ignore[override]
        return self._compare("!==", self._context._checked_value(other))

    def is_null(self) -> JavaScriptBoolean:
        return self._compare("===", None)

    def is_undefined(self) -> JavaScriptBoolean:
        return JavaScriptBoolean(
            self._context, f"({self.as_javascript()} === undefined)"
        )

    def get(
        self, name: str, result_type: type[H], *, writable: bool = False
    ) -> H:
        ctx = self._context
        value = result_type(
            ctx, f"{ctx._render(self)}[{as_javascript_expression(name)}]"
        )
        value._writable = writable
        return value

    def set(self, name: str, value: JavaScriptValue) -> None:
        ctx = self._context
        target = f"{ctx._render(self)}[{as_javascript_expression(name)}]"
        expression = ctx._render(value)
        ctx._emit(f"{target} = {expression};")

    def call_method(
        self,
        name: str,
        *arguments: JavaScriptValue,
        returns: type[H],
    ) -> H:
        ctx = self._context
        method = f"{ctx._render(self)}[{as_javascript_expression(name)}]"
        return ctx._call(method, arguments, returns)


Number: TypeAlias = Union[int, float, "JavaScriptNumber"]
String: TypeAlias = Union[str, "JavaScriptString"]
Boolean: TypeAlias = Union[bool, "JavaScriptBoolean"]


class JavaScriptBoolean(JavaScriptHandle[bool]):
    def and_then(
        self, predicate: Boolean | Callable[[], Boolean]
    ) -> JavaScriptBoolean:
        """Short-circuit a predicate, including any calls it records."""
        ctx = self._context
        return JavaScriptBoolean(
            ctx, f"({ctx._render(self)} && {ctx._predicate(predicate)})"
        )

    def or_else(
        self, predicate: Boolean | Callable[[], Boolean]
    ) -> JavaScriptBoolean:
        ctx = self._context
        return JavaScriptBoolean(
            ctx, f"({ctx._render(self)} || {ctx._predicate(predicate)})"
        )

    def __and__(self, other: Boolean) -> JavaScriptBoolean:
        return self._compare("&&", other)

    def __rand__(self, other: Boolean) -> JavaScriptBoolean:
        return JavaScriptBoolean(
            self._context,
            f"({self._context._render(other)} && {self.as_javascript()})",
        )

    def __or__(self, other: Boolean) -> JavaScriptBoolean:
        return self._compare("||", other)

    def __ror__(self, other: Boolean) -> JavaScriptBoolean:
        return JavaScriptBoolean(
            self._context,
            f"({self._context._render(other)} || {self.as_javascript()})",
        )

    def __invert__(self) -> JavaScriptBoolean:
        return JavaScriptBoolean(self._context, f"(!{self.as_javascript()})")


class JavaScriptNumber(JavaScriptHandle[float]):
    def _binary(self, operator: str, other: Number) -> JavaScriptNumber:
        ctx = self._context
        return JavaScriptNumber(
            ctx, f"({ctx._render(self)} {operator} {ctx._render(other)})"
        )

    def _reverse(self, operator: str, other: Number) -> JavaScriptNumber:
        ctx = self._context
        return JavaScriptNumber(
            ctx, f"({ctx._render(other)} {operator} {ctx._render(self)})"
        )

    def _update(self, operator: str, other: Number) -> JavaScriptNumber:
        ctx = self._context
        ctx._make_writable(self)
        ctx._emit(f"{ctx._render(self)} {operator}= {ctx._render(other)};")
        return self

    def __add__(self, other: Number) -> JavaScriptNumber:
        return self._binary("+", other)

    def __radd__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("+", other)

    def __sub__(self, other: Number) -> JavaScriptNumber:
        return self._binary("-", other)

    def __rsub__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("-", other)

    def __mul__(self, other: Number) -> JavaScriptNumber:
        return self._binary("*", other)

    def __rmul__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("*", other)

    def __truediv__(self, other: Number) -> JavaScriptNumber:
        return self._binary("/", other)

    def __rtruediv__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("/", other)

    def __mod__(self, other: Number) -> JavaScriptNumber:
        return self._binary("%", other)

    def __rmod__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("%", other)

    def __pow__(self, other: Number) -> JavaScriptNumber:
        return self._binary("**", other)

    def __rpow__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("**", other)

    def __and__(self, other: Number) -> JavaScriptNumber:
        return self._binary("&", other)

    def __or__(self, other: Number) -> JavaScriptNumber:
        return self._binary("|", other)

    def __xor__(self, other: Number) -> JavaScriptNumber:
        return self._binary("^", other)

    def __lshift__(self, other: Number) -> JavaScriptNumber:
        return self._binary("<<", other)

    def __rshift__(self, other: Number) -> JavaScriptNumber:
        return self._binary(">>", other)

    def __rand__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("&", other)

    def __ror__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("|", other)

    def __rxor__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("^", other)

    def __rlshift__(self, other: Number) -> JavaScriptNumber:
        return self._reverse("<<", other)

    def __rrshift__(self, other: Number) -> JavaScriptNumber:
        return self._reverse(">>", other)

    def __neg__(self) -> JavaScriptNumber:
        return JavaScriptNumber(self._context, f"(-{self.as_javascript()})")

    def __pos__(self) -> JavaScriptNumber:
        return JavaScriptNumber(self._context, f"(+{self.as_javascript()})")

    def __invert__(self) -> JavaScriptNumber:
        return JavaScriptNumber(self._context, f"(~{self.as_javascript()})")

    def __iadd__(self, other: Number) -> JavaScriptNumber:
        return self._update("+", other)

    def __isub__(self, other: Number) -> JavaScriptNumber:
        return self._update("-", other)

    def __imul__(self, other: Number) -> JavaScriptNumber:
        return self._update("*", other)

    def __itruediv__(self, other: Number) -> JavaScriptNumber:
        return self._update("/", other)

    def __imod__(self, other: Number) -> JavaScriptNumber:
        return self._update("%", other)

    def __ipow__(self, other: Number) -> JavaScriptNumber:
        return self._update("**", other)

    def __iand__(self, other: Number) -> JavaScriptNumber:
        return self._update("&", other)

    def __ior__(self, other: Number) -> JavaScriptNumber:
        return self._update("|", other)

    def __ixor__(self, other: Number) -> JavaScriptNumber:
        return self._update("^", other)

    def __ilshift__(self, other: Number) -> JavaScriptNumber:
        return self._update("<<", other)

    def __irshift__(self, other: Number) -> JavaScriptNumber:
        return self._update(">>", other)

    def __lt__(self, other: Number) -> JavaScriptBoolean:
        return self._compare("<", other)

    def __le__(self, other: Number) -> JavaScriptBoolean:
        return self._compare("<=", other)

    def __gt__(self, other: Number) -> JavaScriptBoolean:
        return self._compare(">", other)

    def __ge__(self, other: Number) -> JavaScriptBoolean:
        return self._compare(">=", other)


class JavaScriptString(JavaScriptHandle[str]):
    @property
    def length(self) -> JavaScriptNumber:
        return self.get("length", JavaScriptNumber)

    def __add__(self, other: String) -> JavaScriptString:
        ctx = self._context
        return JavaScriptString(
            ctx, f"({ctx._render(self)} + {ctx._render(other)})"
        )

    def __radd__(self, other: String) -> JavaScriptString:
        ctx = self._context
        return JavaScriptString(
            ctx, f"({ctx._render(other)} + {ctx._render(self)})"
        )

    def __iadd__(self, other: String) -> JavaScriptString:
        ctx = self._context
        ctx._make_writable(self)
        ctx._emit(f"{ctx._render(self)} += {ctx._render(other)};")
        return self

    def __lt__(self, other: String) -> JavaScriptBoolean:
        return self._compare("<", other)

    def __le__(self, other: String) -> JavaScriptBoolean:
        return self._compare("<=", other)

    def __gt__(self, other: String) -> JavaScriptBoolean:
        return self._compare(">", other)

    def __ge__(self, other: String) -> JavaScriptBoolean:
        return self._compare(">=", other)

    def includes(self, value: String) -> JavaScriptBoolean:
        return self.call_method("includes", value, returns=JavaScriptBoolean)

    def to_lower_case(self) -> JavaScriptString:
        return self.call_method("toLowerCase", returns=JavaScriptString)

    def to_upper_case(self) -> JavaScriptString:
        return self.call_method("toUpperCase", returns=JavaScriptString)

    def trim(self) -> JavaScriptString:
        return self.call_method("trim", returns=JavaScriptString)


class JavaScriptObject(JavaScriptHandle[object]):
    """An object whose members are accessed explicitly with get/set."""


class JavaScriptUndefined(JavaScriptHandle[None]):
    """The result of a JavaScript function returning no value."""


class JavaScriptNullable(JavaScriptHandle[object], Generic[H]):
    """A nullable value requiring an explicit checked unwrap."""

    def __init__(
        self, context: CompileContext, expression: str, value_type: type[H]
    ) -> None:
        super().__init__(context, expression)
        self._value_type = value_type

    def _copy(self, expression: str) -> JavaScriptNullable[H]:
        return JavaScriptNullable(self._context, expression, self._value_type)

    def unwrap(self) -> H:
        ctx = self._context
        result = ctx._bind(self._value_type(ctx, ctx._render(self)))
        ctx._emit(
            f"if ({ctx._render(result)} == null) "
            '{ throw new Error("Expected a non-null JavaScript value"); }'
        )
        return result


class JavaScriptArray(JavaScriptHandle[object], Generic[H]):
    def __init__(
        self, context: CompileContext, expression: str, item_type: type[H]
    ) -> None:
        super().__init__(context, expression)
        self.item_type = item_type

    def _copy(self, expression: str) -> JavaScriptArray[H]:
        return JavaScriptArray(self._context, expression, self.item_type)

    @property
    def length(self) -> JavaScriptNumber:
        return self.get("length", JavaScriptNumber)

    def __getitem__(self, index: Number) -> JavaScriptNullable[H]:
        ctx = self._context
        return JavaScriptNullable(
            ctx,
            f"{ctx._render(self)}[{ctx._render(index)}]",
            self.item_type,
        )

    def __setitem__(self, index: Number, value: H) -> None:
        ctx = self._context
        ctx._emit(
            f"{ctx._render(self)}[{ctx._render(index)}] = {ctx._render(value)};"
        )

    def push(self, *values: H) -> JavaScriptNumber:
        return self.call_method("push", *values, returns=JavaScriptNumber)

    def pop(self) -> JavaScriptNullable[H]:
        ctx = self._context
        result = ctx._call(f"{ctx._render(self)}.pop", (), JavaScriptObject)
        return JavaScriptNullable(ctx, ctx._render(result), self.item_type)


class JavaScriptFunction(JavaScriptHandle[object], Generic[R_co]):
    """A function with an explicit result type and parameter handle types."""

    def __init__(
        self,
        context: CompileContext,
        expression: str,
        returns: type[R_co],
        parameters: Mapping[str, type[JavaScriptHandle[object]]],
    ) -> None:
        super().__init__(context, expression)
        self.returns = returns
        self.parameters = dict(parameters)
        self._body_scope: tuple[int, ...] | None = None

    def _copy(self, expression: str) -> JavaScriptFunction[R_co]:
        return JavaScriptFunction(
            self._context, expression, self.returns, self.parameters
        )

    def __call__(self, *arguments: JavaScriptValue) -> R_co:
        if len(arguments) != len(self.parameters):
            raise TypeError(
                "Incorrect number of JavaScript function arguments"
            )
        for argument, expected in zip(arguments, self.parameters.values()):
            if not self._context._matches(argument, expected):
                raise TypeError(f"Expected a {expected.__name__} argument")
        return self._context._call(
            self._context._render(self), arguments, self.returns
        )

    def parameter(self, name: str, value_type: type[H]) -> H:
        """Get a typed parameter while recording this function's body."""
        if self._body_scope != tuple(self._context._scopes):
            raise RuntimeError(
                "Parameters are only available in the function body"
            )
        if self.parameters.get(name) is not value_type:
            raise TypeError(
                f"Parameter {name!r} does not have the requested type"
            )
        value = value_type(self._context, name)
        value._writable = True
        return value
