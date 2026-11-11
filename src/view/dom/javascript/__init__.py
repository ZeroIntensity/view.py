"""Compile typed Python builders to JavaScript at decoration time.

Calls are recorded once; expressions refer to live JavaScript values. Use
CompileContext.variable() to explicitly snapshot a property or expression.
Python control flow runs during compilation. Runtime branches and loops use
condition().if_true(), condition().if_false(), and condition().while_true().
"""

from ._compiler import (
    CompileContext,
    Condition,
    Switch,
    TryBlock,
    javascript_compiler,
)
from ._dom import (
    Console,
    Document,
    Element,
    Event,
    EventTarget,
    InputElement,
    Window,
)
from ._values import (
    Boolean,
    JavaScriptArray,
    JavaScriptBoolean,
    JavaScriptFunction,
    JavaScriptHandle,
    JavaScriptNullable,
    JavaScriptNumber,
    JavaScriptObject,
    JavaScriptString,
    JavaScriptUndefined,
    JavaScriptValue,
    Number,
    String,
    SupportsJavaScript,
    as_javascript_expression,
)

__all__ = (
    "Boolean",
    "CompileContext",
    "Condition",
    "Console",
    "Document",
    "Element",
    "Event",
    "EventTarget",
    "InputElement",
    "JavaScriptArray",
    "JavaScriptBoolean",
    "JavaScriptFunction",
    "JavaScriptHandle",
    "JavaScriptNullable",
    "JavaScriptNumber",
    "JavaScriptObject",
    "JavaScriptString",
    "JavaScriptUndefined",
    "JavaScriptValue",
    "Number",
    "String",
    "SupportsJavaScript",
    "Switch",
    "TryBlock",
    "Window",
    "as_javascript_expression",
    "javascript_compiler",
)
