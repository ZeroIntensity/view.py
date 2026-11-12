"""Recording contexts, lexical scopes, and JavaScript control flow."""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import TypeAlias, TypeVar, cast, overload

from typing_extensions import Self

from view.dom.javascript._dom import Console, Document, Window
from view.dom.javascript._values import (
    Boolean,
    JavaScriptArray,
    JavaScriptBoolean,
    JavaScriptFunction,
    JavaScriptHandle,
    JavaScriptNumber,
    JavaScriptObject,
    JavaScriptString,
    JavaScriptUndefined,
    JavaScriptValue,
    Number,
    String,
    as_javascript_expression,
)

H = TypeVar("H", bound=JavaScriptHandle[object])
Predicate: TypeAlias = Boolean | Callable[[], Boolean]

# Reserved words cannot be declaration names, even though some are properties.
_RESERVED = frozenset(
    [
        "await",
        "break",
        "case",
        "catch",
        "class",
        "const",
        "continue",
        "debugger",
        "default",
        "delete",
        "do",
        "else",
        "enum",
        "export",
        "extends",
        "false",
        "finally",
        "for",
        "function",
        "if",
        "implements",
        "import",
        "in",
        "instanceof",
        "interface",
        "let",
        "new",
        "null",
        "package",
        "private",
        "protected",
        "public",
        "return",
        "static",
        "super",
        "switch",
        "this",
        "throw",
        "true",
        "try",
        "typeof",
        "var",
        "void",
        "while",
        "with",
        "yield",
        "eval",
        "arguments",
    ]
)


def _identifier(name: str) -> None:
    if (
        not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", name)
        or name in _RESERVED
        or name.startswith("__view_py_")
    ):
        raise ValueError(
            f"Invalid or reserved JavaScript identifier: {name!r}"
        )


class CompileContext:
    """Record JavaScript once by executing a Python builder.

    Calls are evaluated once into generated variables. Arithmetic, comparisons,
    and property handles are expressions; use variable() for a snapshot. Use a
    callable condition when calls themselves must run on every loop iteration.
    raw(), expression(), and typed get/set/call_method cover additional syntax
    and JavaScript APIs without accepting arbitrary Python attribute typos.
    """

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._scopes: list[int] = []
        self._blocks: list[str] = []
        self._returns: list[type[JavaScriptHandle[object]]] = []
        self._counter = 0
        self._scope_counter = 0
        self._indent = 0
        self._closed = False
        self._tries: list[TryBlock] = []
        self._document = Document(self, "document")
        self._window = Window(self, "window")
        self._console = Console(self, "console")

    @property
    def document(self) -> Document:
        return self._document

    @property
    def window(self) -> Window:
        return self._window

    @property
    def console(self) -> Console:
        return self._console

    def _active(self) -> None:
        if self._closed:
            raise RuntimeError(
                "This JavaScript compilation has already finished"
            )

    def _validate(self, value: JavaScriptHandle[object]) -> None:
        if value._context is not self:
            raise ValueError(
                "Cannot mix handles from different compile contexts"
            )
        if tuple(self._scopes[: len(value._scope)]) != value._scope:
            raise ValueError("A JavaScript handle escaped its lexical scope")

    def _checked_value(self, value: object) -> JavaScriptValue:
        # Validate before narrowing object, e.g. the argument to __eq__.
        as_javascript_expression(cast("JavaScriptValue", value))
        return cast("JavaScriptValue", value)

    def _render(self, value: JavaScriptValue) -> str:
        self._active()
        if isinstance(value, JavaScriptHandle):
            handle = cast("JavaScriptHandle[object]", value)
            self._validate(handle)
            return as_javascript_expression(handle)
        # Walk collections as well: nested handles must belong to this scope.
        if isinstance(value, Mapping):
            for item in value.values():
                self._render(item)
        elif isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        ):
            for item in value:
                self._render(item)
        return as_javascript_expression(value)

    def _emit(self, line: str) -> None:
        self._active()
        self._lines.append("    " * self._indent + line)

    def _name(self) -> str:
        name = f"__view_py_name_{self._counter}"
        self._counter += 1
        return name

    def _bind(self, value: H) -> H:
        expression = self._render(value)
        name = self._name()
        self._emit(f"let {name} = {expression};")
        result = value._copy(name)
        result._writable = True
        return result

    def _make_writable(self, value: JavaScriptHandle[object]) -> None:
        self._validate(value)
        if not value._writable:
            bound = self._bind(value)
            value._expression = bound._expression
            value._scope = bound._scope
            value._writable = True

    def _call(
        self,
        target: str,
        arguments: Sequence[JavaScriptValue],
        result_type: type[H],
    ) -> H:
        args = ", ".join(self._render(arg) for arg in arguments)
        return self._bind(result_type(self, f"{target}({args})"))

    @contextmanager
    def _block(self, header: str, kind: str = "block") -> Iterator[None]:
        self._emit(header + " {")
        self._indent += 1
        self._scope_counter += 1
        self._scopes.append(self._scope_counter)
        self._blocks.append(kind)
        try:
            yield
        finally:
            self._blocks.pop()
            self._scopes.pop()
            self._indent -= 1
            self._emit("}")

    def _predicate(self, predicate: Predicate) -> str:
        if not callable(predicate):
            if not isinstance(predicate, (bool, JavaScriptBoolean)):
                raise TypeError("A condition must be a JavaScript boolean")
            return self._render(predicate)
        # Capture callback statements in an IIFE, so calls in a loop predicate
        # are reevaluated at runtime along with the final boolean expression.
        lines = self._lines
        indent = self._indent
        self._lines = []
        self._indent = 0
        self._scope_counter += 1
        self._scopes.append(self._scope_counter)
        self._blocks.append("predicate")
        try:
            value = predicate()
            if not isinstance(value, (bool, JavaScriptBoolean)):
                raise TypeError("A condition callback must return a boolean")
            expression = self._render(value)
            body = "\n".join(self._lines)
        finally:
            self._lines = lines
            self._indent = indent
            self._scopes.pop()
            self._blocks.pop()
        return f"(() => {{\n{body}\nreturn {expression};\n}})()"

    def condition(self, predicate: Predicate) -> Condition:
        """Build a condition with if_true(), if_false(), and while_true()."""
        self._active()
        return Condition(self, predicate)

    @overload
    # bool subclasses int in Python, whereas JavaScript has distinct types.
    def variable(  # pyright: ignore[reportOverlappingOverload]
        self,
        value: bool,  # noqa: FBT001
    ) -> JavaScriptBoolean: ...

    @overload
    def variable(self, value: float) -> JavaScriptNumber: ...

    @overload
    def variable(self, value: str) -> JavaScriptString: ...

    @overload
    def variable(self, value: H) -> H: ...

    @overload
    def variable(self, value: JavaScriptValue) -> JavaScriptHandle[object]: ...

    def variable(self, value: JavaScriptValue) -> JavaScriptHandle[object]:
        """Snapshot an expression into a mutable JavaScript variable."""
        if isinstance(value, JavaScriptHandle):
            return self._bind(cast("JavaScriptHandle[object]", value))
        if isinstance(value, bool):
            value_type = JavaScriptBoolean
        elif isinstance(value, (int, float)):
            value_type = JavaScriptNumber
        elif isinstance(value, str):
            value_type = JavaScriptString
        else:
            value_type = JavaScriptObject
        return self._bind(value_type(self, self._render(value)))

    @staticmethod
    def _matches(
        value: JavaScriptValue, expected: type[JavaScriptHandle[object]]
    ) -> bool:
        if isinstance(value, JavaScriptHandle):
            return isinstance(value, expected)
        if expected is JavaScriptNumber:
            return isinstance(value, (int, float)) and not isinstance(
                value, bool
            )
        if expected is JavaScriptString:
            return isinstance(value, str)
        if expected is JavaScriptBoolean:
            return isinstance(value, bool)
        return expected in (JavaScriptObject, JavaScriptHandle)

    @overload
    def assign(self, target: JavaScriptBoolean, value: Boolean) -> None: ...

    @overload
    def assign(self, target: JavaScriptNumber, value: Number) -> None: ...

    @overload
    def assign(self, target: JavaScriptString, value: String) -> None: ...

    @overload
    def assign(self, target: H, value: H) -> None: ...

    def assign(
        self, target: JavaScriptHandle[object], value: JavaScriptValue
    ) -> None:
        """Assign to an existing variable without rebinding the Python name."""
        if not self._matches(value, type(target)):
            raise TypeError("Assigned value does not match the target's type")
        self._make_writable(target)
        self._emit(f"{self._render(target)} = {self._render(value)};")

    def number(self, value: JavaScriptValue = 0) -> JavaScriptNumber:
        return self._call("Number", (value,), JavaScriptNumber)

    def string(self, value: JavaScriptValue = "") -> JavaScriptString:
        return self._call("String", (value,), JavaScriptString)

    def boolean(
        self,
        value: JavaScriptValue = False,  # noqa: FBT002
    ) -> JavaScriptBoolean:
        return self._call("Boolean", (value,), JavaScriptBoolean)

    def parse_int(
        self, value: String | Number, radix: Number = 10
    ) -> JavaScriptNumber:
        return self._call("parseInt", (value, radix), JavaScriptNumber)

    def parse_float(self, value: String | Number) -> JavaScriptNumber:
        return self._call("parseFloat", (value,), JavaScriptNumber)

    def array(
        self, values: Sequence[H], item_type: type[H]
    ) -> JavaScriptArray[H]:
        if not all(isinstance(value, item_type) for value in values):
            raise TypeError("Array items must match item_type")
        return self._bind(
            JavaScriptArray(self, self._render(values), item_type)
        )

    def reference(self, name: str, value_type: type[H]) -> H:
        """Refer to an externally defined, typed global binding."""
        _identifier(name)
        return value_type(self, name)

    def expression(self, source: str, value_type: type[H]) -> H:
        """Trust a raw expression and explicitly declare its result type."""
        self._active()
        if not source.strip():
            raise ValueError("An expression cannot be empty")
        return value_type(self, f"({source})")

    def raw(self, source: str) -> None:
        """Emit trusted statements, including JavaScript syntax not wrapped here."""
        for line in source.splitlines():
            self._emit(line)

    def new(
        self,
        constructor: JavaScriptHandle[object],
        *arguments: JavaScriptValue,
        returns: type[H],
    ) -> H:
        return self._call(
            f"new ({self._render(constructor)})", arguments, returns
        )

    @contextmanager
    def for_of(self, array: JavaScriptArray[H]) -> Iterator[H]:
        name = self._name()
        expression = self._render(array)
        with self._block(f"for (let {name} of {expression})", "loop"):
            value = array.item_type(self, name)
            value._writable = True
            yield value

    @contextmanager
    def for_in(
        self, value: JavaScriptHandle[object]
    ) -> Iterator[JavaScriptString]:
        name = self._name()
        expression = self._render(value)
        with self._block(f"for (let {name} in {expression})", "loop"):
            yield JavaScriptString(self, name)

    def _in_loop(self, *, allow_switch: bool = False) -> bool:
        for kind in reversed(self._blocks):
            if kind in ("function", "predicate"):
                return False
            if kind == "loop":
                return True
            if allow_switch and kind == "switch":
                return True
        return False

    def break_(self) -> None:
        if not self._in_loop(allow_switch=True):
            raise RuntimeError("break_() requires a loop or switch")
        self._emit("break;")

    def continue_(self) -> None:
        if not self._in_loop():
            raise RuntimeError(
                "continue_() requires a loop in the current function"
            )
        self._emit("continue;")

    @contextmanager
    def function(
        self,
        parameters: Mapping[str, type[JavaScriptHandle[object]]],
        *,
        returns: type[H],
    ) -> Iterator[JavaScriptFunction[H]]:
        """Declare a function, then record its body using parameter()/return_()."""
        for name in parameters:
            _identifier(name)
        name = self._name()
        function = JavaScriptFunction(self, name, returns, parameters)
        with self._block(
            f"function {name}({', '.join(parameters)})", "function"
        ):
            function._body_scope = tuple(self._scopes)
            self._returns.append(returns)
            try:
                yield function
                if returns is not JavaScriptUndefined:
                    self._emit(
                        'throw new Error("JavaScript function ended without '
                        'returning a value");'
                    )
            finally:
                self._returns.pop()
                function._body_scope = None

    def return_(self, value: JavaScriptValue = None) -> None:
        boundary = next(
            (
                kind
                for kind in reversed(self._blocks)
                if kind in ("function", "predicate")
            ),
            None,
        )
        if not self._returns or boundary != "function":
            raise RuntimeError("return_() requires a JavaScript function body")
        if self._returns[-1] is JavaScriptUndefined and value is None:
            self._emit("return;")
            return
        if not self._matches(value, self._returns[-1]):
            raise TypeError(
                "Return value does not match the function's result type"
            )
        self._emit(f"return {self._render(value)};")

    def throw(self, value: JavaScriptValue) -> None:
        self._emit(f"throw {self._render(value)};")

    @contextmanager
    def switch(self, value: JavaScriptValue) -> Iterator[Switch]:
        """Record case()/default() blocks; use break_() to prevent fallthrough."""
        with self._block(f"switch ({self._render(value)})", "switch"):
            yield Switch(self)

    @contextmanager
    def try_(self) -> Iterator[TryBlock]:
        """Record try, followed by catch() and/or finally_() on the result."""
        block = TryBlock(self)
        self._tries.append(block)
        with self._block("try"):
            yield block
        block._end = len(self._lines)

    def as_javascript(self) -> str:
        if self._scopes:
            raise RuntimeError("Cannot render JavaScript with unclosed blocks")
        if any(not block._handled for block in self._tries):
            raise RuntimeError("Every try_() requires catch() or finally_()")
        return "".join(line + "\n" for line in self._lines)


class Switch:
    """A switch body with explicit JavaScript fallthrough semantics."""

    def __init__(self, context: CompileContext) -> None:
        self._context = context
        self._scope = tuple(context._scopes)
        self._default = False

    def _validate(self) -> None:
        if tuple(self._context._scopes) != self._scope:
            raise RuntimeError("Cases must be directly inside their switch")

    @contextmanager
    def case(self, value: JavaScriptValue) -> Iterator[None]:
        self._validate()
        with self._context._block(f"case {self._context._render(value)}:"):
            yield

    @contextmanager
    def default(self) -> Iterator[None]:
        self._validate()
        if self._default:
            raise RuntimeError("A switch can only have one default")
        self._default = True
        with self._context._block("default:"):
            yield


class TryBlock:
    """Attach a catch and/or finally to an immediately preceding try block."""

    def __init__(self, context: CompileContext) -> None:
        self._context = context
        self._scope = tuple(context._scopes)
        self._end: int | None = None
        self._handled = False
        self._caught = False
        self._finalized = False

    def _validate(self) -> None:
        ctx = self._context
        if tuple(ctx._scopes) != self._scope or len(ctx._lines) != self._end:
            raise RuntimeError(
                "Handlers must immediately follow their try/catch"
            )
        if self._finalized:
            raise RuntimeError("No handler may follow finally_()")

    @contextmanager
    def catch(self) -> Iterator[JavaScriptObject]:
        self._validate()
        if self._caught:
            raise RuntimeError("A try block can only have one catch")
        ctx = self._context
        name = ctx._name()
        with ctx._block(f"catch ({name})"):
            yield JavaScriptObject(ctx, name)
        self._caught = self._handled = True
        self._end = len(ctx._lines)

    @contextmanager
    def finally_(self) -> Iterator[None]:
        self._validate()
        ctx = self._context
        with ctx._block("finally"):
            yield
        self._finalized = self._handled = True
        self._end = len(ctx._lines)


class Condition:
    """A reusable runtime condition, optionally grouping adjacent if/else blocks.

    With ``with ctx.condition(number == 42) as condition:``, use
    ``with condition.if_true():`` and ``with condition.if_false():`` for
    branches, or ``with condition.while_true():`` for a loop. An if_false()
    immediately following if_true() becomes its else branch. Used alone,
    if_false() emits an independent negated if.
    """

    def __init__(self, context: CompileContext, predicate: Predicate) -> None:
        self._context = context
        self._predicate_value = predicate
        self._scope = tuple(context._scopes)
        self._if_end: int | None = None
        self._entered = False

    def _validate(self) -> None:
        self._context._active()
        if tuple(self._context._scopes) != self._scope:
            raise RuntimeError(
                "Use condition branches in their original scope"
            )

    def __enter__(self) -> Self:
        self._validate()
        if self._entered:
            raise RuntimeError("A condition context is already open")
        self._entered = True
        return self

    def __exit__(self, *_: object) -> None:
        self._entered = False

    @contextmanager
    def if_true(self) -> Iterator[None]:
        self._validate()
        ctx = self._context
        expression = ctx._predicate(self._predicate_value)
        with ctx._block(f"if ({expression})"):
            yield
        self._if_end = len(ctx._lines)

    @contextmanager
    def if_false(self) -> Iterator[None]:
        self._validate()
        ctx = self._context
        if self._if_end is not None:
            if len(ctx._lines) != self._if_end:
                raise RuntimeError(
                    "if_false() must immediately follow if_true()"
                )
            header = "else"
        else:
            expression = ctx._predicate(self._predicate_value)
            header = f"if (!({expression}))"
        self._if_end = None
        with ctx._block(header):
            yield

    @contextmanager
    def while_true(self) -> Iterator[None]:
        self._validate()
        ctx = self._context
        expression = ctx._predicate(self._predicate_value)
        with ctx._block(f"while ({expression})", "loop"):
            yield


def javascript_compiler(function: Callable[[CompileContext], None]) -> str:
    """Execute a synchronous builder once and replace it with JavaScript source.

    The result is a string suitable for HTML event attributes and script nodes.
    Python return values and generators are rejected to catch accidental use
    of the previous string-yielding compiler API.
    """
    if inspect.iscoroutinefunction(function) or inspect.isgeneratorfunction(
        function
    ):
        raise TypeError(
            "A JavaScript builder must be a regular synchronous function"
        )
    context = CompileContext()
    try:
        result = function(context)
        if result is not None:
            raise TypeError("A JavaScript builder must return None")
        return context.as_javascript()
    finally:
        context._closed = True
