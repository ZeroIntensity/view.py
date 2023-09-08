from __future__ import annotations

import ast
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from types import CodeType as Code
from types import FrameType as Frame
from types import ModuleType
from typing import Any, Callable, Dict, Union

from .__about__ import __version__

SourceCodeLike = Union[str, Code, Frame, Callable[..., Any], ModuleType]


def pre(data: str, identifier: str | None = None):
    if identifier:
        identifier += "_"

    return f"__view_py_{identifier or ''}{data}"


def nm(name: str):
    return pre(name, "name")


def _flatten(source: list[Symbol]) -> str:
    res = ""

    for i in source:
        res += i.code() + "\n"

    return res


B_OPEN: str = "{"
B_CLOSE: str = "}"


def _err(name: str):
    return f"class {nm(name)} extends Error {B_OPEN}{B_CLOSE};"


def _issubclass(item: Any, tp: type[Any]) -> bool:
    try:
        return issubclass(item, tp)
    except TypeError:
        return False


_ERRORS: list[str] = [
    k for k, v in globals().items() if _issubclass(v, BaseException)
]
ERRORS = "\n".join([_err(i) for i in _ERRORS])
PRINT = f"""function {nm('print')}(posargs, kwargs) {B_OPEN}
    if (kwargs.sep) {B_OPEN}
        throw new Error('passing sep is not possible in javascript');
    {B_CLOSE}
    if (kwargs.end) {B_OPEN}
        throw new Error('passing end is not possible in javascript');
    {B_CLOSE}
    if (kwargs.file) {B_OPEN}
        throw new Error('passing file is not possible in javascript');
    {B_CLOSE}
    if (kwargs.flush) {B_OPEN}
        throw new Error('passing flush is not possible in javascript');
    {B_CLOSE}
    console.log(...posargs)
{B_CLOSE}"""
BOOL = f"""function {pre('bool')}(v) {B_OPEN}
    if (v.length === 0) return false;
    if (JSON.stringify(v) === '{B_OPEN}{B_CLOSE}') return false;
    return !!v
{B_CLOSE}"""
ASSERT = f"""function {pre('assert')}(v, msg) {B_OPEN}
    if (!{pre('bool')}(v))
        throw new Error(msg ? `assertion failed: ${B_OPEN}v{B_CLOSE}` : msg)
    return v;
{B_CLOSE}"""
PRESOURCE = "\n".join((BOOL, ASSERT, PRINT, ERRORS))
NAMEDEXPR = f"""function {pre('namedexpr')}(scope, name, v) {B_OPEN}
    scope[name] = v;
{B_CLOSE}"""

NEWLINE = "\n"


class Symbol(ABC):
    @abstractmethod
    def code(self) -> str:
        ...

    @property
    def names(self) -> list[str]:
        # this is SUPER hacky, but i guess its ok since this api isnt public
        frame = inspect.currentframe()
        assert frame, "failed to get frame"
        assert frame.f_back, "frame has no f_back"
        back = frame.f_back
        real_back = back.f_back
        assert real_back, "frame has no f_back"

        return real_back.f_locals["self"]._names

    _names = []


class Source(Symbol):
    def __init__(self, text: str) -> None:
        self.text = text

    def code(self) -> str:
        return self.text


Parameters = Dict[str, Union[str, None]]


class FunctionBody(Symbol):
    def __init__(
        self,
        pos_args: Parameters,
        args: Parameters,
        kw_args: Parameters,
        varg: str | None,
        vkwarg: str | None,
        source: list[Symbol],
    ) -> None:
        self.pos_args = pos_args
        self.args = args
        self.kw_args = kw_args
        self.varg = varg
        self.vkwarg = vkwarg
        self.source = source

    def code(self) -> str:
        src = _flatten(self.source)
        pindex = pre("pindex")
        params = f"let {pindex} = 0;"

        for k, v in self.kw_args.items():
            df_str = (
                f"{nm(k)} = {v}"
                if v
                else f"throw new Error('missing keyword argument for {k}')"
            )
            params += f"""\n
let {nm(k)};
if (kwargs['{k}'] === undefined) {B_OPEN}
    {df_str}
{B_CLOSE} else {B_OPEN}
    {nm(k)} = kwargs['{k}'];
    delete kwargs['{k}'];
{B_CLOSE}
"""

        for k, v in self.pos_args.items():
            df_str = (
                f"{nm(k)} = {v}"
                if v
                else f"throw new Error('missing positional argument for {k}')"
            )
            params += f"""let {nm(k)};
if (args[{pindex}++] === undefined) {B_OPEN}
    {df_str}
{B_CLOSE} else {B_OPEN}
    {nm(k)} = args[{pindex}];
{B_CLOSE}
"""

        for k, v in self.args.items():
            df_str = (
                f"{nm(k)} = {v}"
                if v
                else f"throw new Error('missing argument for {k}')"
            )

            params += f"""let {nm(k)};
if (kwargs['{k}'] === undefined) {B_OPEN}
    if (args[{pindex}++] === undefined) {B_OPEN}
        {df_str}
    {B_CLOSE} else {B_OPEN}
        {nm(k)} = args[{pindex}];
    {B_CLOSE}
{B_CLOSE} else {B_OPEN}
    {nm(k)} = kwargs['{k}'];
    delete kwargs['{k}'];
{B_CLOSE}
"""

        if self.varg:
            params += (
                f"\nlet {nm(self.varg)} = args.slice"
                f"({pindex}, args.length + 1);\n"
            )

        if self.vkwarg:
            params += f"\nlet {nm(self.vkwarg)} = kwargs;\n"

        return f"""{B_OPEN}
    {params}
    {src}
{B_CLOSE}"""


class FunctionSignature(Symbol):
    def __init__(self, name: str):
        self.name = name
        self.names.append(nm(name))
        self.decl = "function"

    def code(self) -> str:
        return f"{self.decl} {nm(self.name)}(args, kwargs)"


class SymbolWrapping(Symbol):
    def __init__(self, *args: Symbol) -> None:
        self.symbols = args

    def code(self) -> str:
        return "\n".join([i.code() for i in self.symbols])


class Assignment(Symbol):
    def __init__(self, name: str, value: str, decl: str = "let") -> None:
        self.name = name
        self.value = value
        self.decl = decl
        self.names.append(name)

    def code(self) -> str:
        return f"{self.decl} {self.name} = {self.value}"


class Call(Symbol):
    def __init__(self, name: str, args: list[str], kwds: dict[str, str]):
        self.name = name
        self.args = args
        self.kwds = kwds

    def code(self) -> str:
        kwds = ""

        for k, v in self.kwds.items():
            kwds += f"{k}: {v},"

        if kwds:
            kwds = kwds[:-1]

        return (
            f"{self.name}"
            f"([{', '.join(self.args)}], {B_OPEN}{kwds}{B_CLOSE})"
        )


class If(Symbol):
    def __init__(self, cond: Symbol, body: list[Symbol], orelse: list[Symbol]):
        self.cond = cond
        self.body = body
        self.orelse = orelse

    def code(self) -> str:
        elsestr = ""
        if self.orelse:
            elsestr = f"else {B_OPEN}{_flatten(self.orelse)}{B_CLOSE}"

        return (
            f"if ({self.cond.code()}) "
            f"{B_OPEN}{_flatten(self.body)}{B_CLOSE}{elsestr}"
        )


class For(Symbol):
    def __init__(self, target: str, iter: str, body: list[Symbol]):
        self.target = target
        self.iter = iter
        self.body = body

    def code(self) -> str:
        return f"""for (const {self.target} of {self.iter})
{B_OPEN}
{_flatten(self.body)}
{B_CLOSE}"""


class Compare(Symbol):
    def __init__(self, left: str, ops: list[str], comps: list[Symbol]):
        self.left = left
        self.ops = ops
        self.comps = comps

    def code(self) -> str:
        result = self.left

        for op, comp in zip(self.ops, self.comps):
            result += f"{op} {comp.code()}"

        return result


def call(target: str, args: str) -> str:
    return f"{target}({args})"


class _Compiler:
    def __init__(self):
        self.source: list[Symbol] = []
        self._names: list[str] = []

    def _translate_bo(self, node: ast.BoolOp):
        s = ""

        for i in node.values:
            s += call(pre("bool"), self.translate_expr(i).code())

            if node.op is ast.And:
                s += "&&"
            else:
                s += "||"

        return Source(s)

    def _translate_fd(self, node: ast.FunctionDef):
        sig = FunctionSignature(node.name)
        pos_only: Parameters = {}
        args: Parameters = {}
        kw_only: Parameters = {}

        for index, i in enumerate(node.args.kwonlyargs):
            df = node.args.kw_defaults[index]
            kw_only[i.arg] = self.translate_expr(df).code() if df else None

        defaults = node.args.defaults.copy()
        has_default = False
        full_len = len(node.args.posonlyargs) + len(node.args.args)
        for index, value in enumerate(node.args.posonlyargs):
            if len(node.args.defaults) == (full_len - index):
                has_default = True

            if not has_default:
                pos_only[value.arg] = None
            else:
                pos_only[value.arg] = self.translate_expr(
                    defaults.pop(0)
                ).code()

        for index, value in enumerate(node.args.args):
            if len(node.args.defaults) == (full_len - index):
                has_default = True

            if not has_default:
                args[value.arg] = None
            else:
                args[value.arg] = self.translate_expr(defaults.pop(0)).code()

        varg = node.args.vararg.arg if node.args.vararg else None
        vkwarg = node.args.kwarg.arg if node.args.kwarg else None

        body = FunctionBody(
            pos_only,
            args,
            kw_only,
            varg,
            vkwarg,
            self.translate_body(node.body),
        )
        decorators = "\n"

        for i in node.decorator_list:
            decorators += (
                f"{nm(node.name)} = {self.translate_expr(i).code()}"
                f"({nm(node.name)})\n"
            )

        return SymbolWrapping(sig, body, Source(decorators))

    def _translate_name(self, node: ast.Name):
        return Source(nm(node.id))

    def _translate_assign(self, node: ast.Assign):
        targets = []
        value = self.translate_expr(node.value).code()
        for i in node.targets:
            targets.append(Assignment(self.translate_expr(i).code(), value))

        return SymbolWrapping(*targets)

    def _translate_constant(self, node: ast.Constant):
        if isinstance(node.value, bool):
            return Source(str(node.value).lower())

        return Source(repr(node.value))

    def _translate_pass(self, _: ast.Pass):
        return Source("/* pass */")

    def _translate_break(self, _: ast.Break):
        return Source("break")

    def _translate_continue(self, _: ast.Continue):
        return Source("continue")

    def _translate_if(self, node: ast.If):
        return If(
            self.translate_expr(node.test),
            self.translate_body(node.body),
            self.translate_body(node.orelse),
        )

    def _translate_expr_node(self, node: ast.Expr) -> Symbol:
        return self.translate_expr(node.value)

    def _translate_for(self, node: ast.For):
        return For(
            self.translate_expr(node.target).code(),
            self.translate_expr(node.iter).code(),
            self.translate_body(node.body),
        )

    def _translate_assert(self, node: ast.Assert):
        return Source(
            f"{pre('assert')}({pre('bool')}"
            f"({self.translate_expr(node.test).code()}), "
            f"{self.translate_expr(node.msg).code() if node.msg else 'null'})"
        )

    def _translate_compare(self, node: ast.Compare):
        comps = [self.translate_expr(i) for i in node.comparators]
        ops_mapping: dict[type[ast.cmpop], str] = {
            ast.Eq: "===",
            ast.NotEq: "!==",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
            ast.Is: "===",
            ast.IsNot: "!==",
            ast.In: "==",
            ast.NotIn: "==",
        }
        ops = [ops_mapping[type(i)] for i in node.ops]

        return Compare(self.translate_expr(node.left).code(), ops, comps)

    def _translate_call(self, node: ast.Call):
        args = [self.translate_expr(i).code() for i in node.args]
        kwds: dict[str, str] = {  # type: ignore
            arg.arg: self.translate_expr(arg.value).code()
            for arg in node.keywords
        }
        if isinstance(node.func, ast.Name):
            if node.func.id == "_compiler_preserve":
                return Call(node.func.id, args, kwds)

        return Call(self.translate_expr(node.func).code(), args, kwds)

    def _translate_attribute(self, node: ast.Attribute):
        return Source(
            self.translate_expr(node.value).code() + "." + nm(node.attr)
        )

    def _translate_starred(self, node: ast.Starred):
        return f"...{self.translate_expr(node.value).code()}"

    def _translate_await(self, node: ast.Await):
        return f"await {self.translate_expr(node.value).code()}"

    def _translate_afd(self, node: ast.AsyncFunctionDef):
        sym = self._translate_fd(node)  # type: ignore
        assert isinstance(sym.symbols[0], FunctionSignature)
        sym.symbols[0].decl = "async function"
        return sym

    def _translate_named_expr(self, node: ast.NamedExpr):
        return (
            f"{pre('namedexpr')}(this, {self.translate_expr(node.target)}"
            f", {self.translate_expr(node.value).code()})"
        )

    def translate_expr(self, node: ast.expr) -> Symbol:
        translators: dict[type[ast.expr], Callable[[ast.expr], Symbol]] = {
            ast.BoolOp: self._translate_bo,
            ast.NamedExpr: self._translate_named_expr,
            ast.BinOp: ...,
            ast.UnaryOp: ...,
            ast.Lambda: ...,
            ast.IfExp: ...,
            ast.Dict: ...,
            ast.Set: ...,
            ast.ListComp: ...,
            ast.SetComp: ...,
            ast.DictComp: ...,
            ast.GeneratorExp: ...,
            ast.Await: self._translate_await,
            ast.Yield: ...,
            ast.YieldFrom: ...,
            ast.Compare: self._translate_compare,
            ast.Call: self._translate_call,
            ast.FormattedValue: ...,
            ast.JoinedStr: ...,
            ast.Constant: self._translate_constant,
            ast.Attribute: self._translate_attribute,
            ast.Subscript: ...,
            ast.Starred: self._translate_starred,
            ast.Name: self._translate_name,
            ast.List: ...,
            ast.Tuple: ...,
            ast.Slice: ...,
        }
        result = translators[type(node)](node)
        if not isinstance(result, Symbol):
            raise TypeError(
                f"translator for {type(node).__name__} returned non symbol:"
                f"{result!r}"
            )
        return result

    def _translate_import(self, node: ast.Import):
        symbols = []

        for name in node.names:
            module = __import__(name.name)
            if not module.__file__:
                raise TypeError(f"{module} has no __file__")
            ast_mod = ast.parse(
                Path(module.__file__).read_text(encoding="utf-8")
            )
            symbols.append(
                Source(
                    _Compiler.compile_mod(
                        ast_mod,
                        namespace=module.__name__,
                    )
                )
            )

        return SymbolWrapping(*symbols)

    def _translate_return(self, node: ast.Return):
        if not node.value:
            return Source("return")
        return Source(f"return {self.translate_expr(node.value).code()}")

    def translate_stmt(self, node: ast.stmt) -> Symbol:
        translators: dict[type[ast.stmt], Callable[[ast.stmt], Symbol]] = {
            ast.FunctionDef: self._translate_fd,
            ast.AsyncFunctionDef: self._translate_afd,
            ast.ClassDef: ...,
            ast.Return: self._translate_return,
            ast.Delete: ...,
            ast.Assign: self._translate_assign,
            ast.AugAssign: ...,
            ast.For: self._translate_for,
            ast.AsyncFor: ...,
            ast.While: ...,
            ast.If: self._translate_if,
            ast.With: ...,
            ast.AsyncWith: ...,
            ast.Match: ...,
            ast.Raise: ...,
            ast.Try: ...,
            ast.Assert: self._translate_assert,
            ast.Import: self._translate_import,
            ast.ImportFrom: ...,
            ast.Global: ...,
            ast.Nonlocal: ...,
            ast.Expr: self._translate_expr_node,
            ast.Pass: self._translate_pass,
            ast.Break: self._translate_break,
            ast.Continue: self._translate_continue,
        }
        result = translators[type(node)](node)
        if not isinstance(result, Symbol):
            raise TypeError(
                f"translator for {type(node).__name__} returned non symbol:"
                f" {result!r}"
            )
        return result

    def translate_body(self, nodes: list[ast.stmt]) -> list[Symbol]:
        source: list[Symbol] = []
        for i in nodes:
            source.append(self.translate_stmt(i))

        return source

    @classmethod
    def compile_mod(
        cls, mod: ast.Module, *, namespace: str | None = None
    ) -> str:
        self = cls()

        for stmt in mod.body:
            self.source.append(self.translate_stmt(stmt))

        if not namespace:
            return (
                f"// view.py {__version__}\n\n"
                + PRESOURCE
                + "\n\n"
                + self.finalize()
            )
        else:
            return f"""const {nm(namespace)} = (function() {B_OPEN}
{self.finalize()}
return {B_OPEN}
    {','.join(self._names)}
{B_CLOSE}
{B_CLOSE})()"""

    def finalize(self):
        source = ""

        for i in self.source:
            source += i.code() + "\n"

        return source


def _compile(data: str, lock_namespace: bool) -> str:
    mod = ast.parse(data)
    print(ast.dump(mod, indent=4))
    result = _Compiler.compile_mod(mod)

    if not lock_namespace:
        return result

    return "(() => {" + result + "})();"


def compile(source: SourceCodeLike, *, lock_namespace: bool = False) -> str:
    if isinstance(source, str):
        return _compile(source, lock_namespace)

    if isinstance(source, Code):
        return _compile(
            Path(source.co_filename).read_text(encoding="utf-8"),
            lock_namespace,
        )

    if isinstance(source, Frame):
        return _compile(
            Path(source.f_code.co_filename).read_text(encoding="utf-8"),
            lock_namespace,
        )

    if isinstance(source, ModuleType):
        if not source.__file__:
            raise TypeError(f"{source!r} has no __file__")
        return _compile(
            Path(source.__file__).read_text(encoding="utf-8"), lock_namespace
        )

    if callable(source):
        return _compile(inspect.getsource(source), lock_namespace)

    raise TypeError(
        "expected a string, code, frame, module, or callable"
        f" object, but got {source!r}"
    )
