"""Typed browser API handles. Additional APIs use explicit get/call_method."""

from __future__ import annotations

from ._values import (
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
)


class EventTarget(JavaScriptObject):
    def add_event_listener(
        self,
        event: String,
        listener: JavaScriptFunction[JavaScriptHandle[object]],
    ) -> None:
        self.call_method(
            "addEventListener", event, listener, returns=JavaScriptUndefined
        )


class Event(JavaScriptObject):
    @property
    def target(self) -> JavaScriptNullable[EventTarget]:
        return JavaScriptNullable(
            self._context, f"{self.as_javascript()}.target", EventTarget
        )

    def prevent_default(self) -> None:
        self.call_method("preventDefault", returns=JavaScriptUndefined)

    def stop_propagation(self) -> None:
        self.call_method("stopPropagation", returns=JavaScriptUndefined)


class Element(EventTarget):
    """A non-null browser element. DOM lookups check for missing elements."""

    @property
    def inner_html(self) -> JavaScriptString:
        return self.get("innerHTML", JavaScriptString)

    @inner_html.setter
    def inner_html(self, value: String | Number) -> None:
        self.set("innerHTML", value)

    @property
    def text_content(self) -> JavaScriptString:
        return self.get("textContent", JavaScriptString)

    @text_content.setter
    def text_content(self, value: String | Number) -> None:
        self.set("textContent", value)

    @property
    def id(self) -> JavaScriptString:
        return self.get("id", JavaScriptString)

    @id.setter
    def id(self, value: String) -> None:
        self.set("id", value)

    @property
    def class_name(self) -> JavaScriptString:
        return self.get("className", JavaScriptString)

    @class_name.setter
    def class_name(self, value: String) -> None:
        self.set("className", value)

    @property
    def parent_element(self) -> JavaScriptNullable[Element]:
        return JavaScriptNullable(
            self._context, f"{self.as_javascript()}.parentElement", Element
        )

    def get_attribute(
        self, name: String
    ) -> JavaScriptNullable[JavaScriptString]:
        value = self.call_method(
            "getAttribute", name, returns=JavaScriptObject
        )
        return JavaScriptNullable(
            self._context, value.as_javascript(), JavaScriptString
        )

    def set_attribute(self, name: String, value: String | Number) -> None:
        self.call_method(
            "setAttribute", name, value, returns=JavaScriptUndefined
        )

    def remove_attribute(self, name: String) -> None:
        self.call_method("removeAttribute", name, returns=JavaScriptUndefined)

    def append_child(self, child: Element) -> Element:
        return self.call_method("appendChild", child, returns=Element)

    def remove(self) -> None:
        self.call_method("remove", returns=JavaScriptUndefined)

    def query_selector(self, selector: String) -> Element:
        value = self.call_method(
            "querySelector", selector, returns=JavaScriptObject
        )
        return JavaScriptNullable(
            self._context, value.as_javascript(), Element
        ).unwrap()


class InputElement(Element):
    """Properties specific to an HTML input element."""

    @property
    def value(self) -> JavaScriptString:
        return self.get("value", JavaScriptString)

    @value.setter
    def value(self, value: String | Number) -> None:
        self.set("value", value)

    @property
    def checked(self) -> JavaScriptBoolean:
        return self.get("checked", JavaScriptBoolean)

    @checked.setter
    def checked(self, value: bool | JavaScriptBoolean) -> None:
        self.set("checked", value)

    @property
    def disabled(self) -> JavaScriptBoolean:
        return self.get("disabled", JavaScriptBoolean)

    @disabled.setter
    def disabled(self, value: bool | JavaScriptBoolean) -> None:
        self.set("disabled", value)

    def focus(self) -> None:
        self.call_method("focus", returns=JavaScriptUndefined)


class Document(EventTarget):
    @property
    def title(self) -> JavaScriptString:
        return self.get("title", JavaScriptString)

    @title.setter
    def title(self, value: String) -> None:
        self.set("title", value)

    @property
    def body(self) -> Element:
        return JavaScriptNullable(
            self._context, f"{self.as_javascript()}.body", Element
        ).unwrap()

    def get_element_by_id(self, element_id: String) -> Element:
        value = self.call_method(
            "getElementById", element_id, returns=JavaScriptObject
        )
        return JavaScriptNullable(
            self._context, value.as_javascript(), Element
        ).unwrap()

    def query_selector(self, selector: String) -> Element:
        value = self.call_method(
            "querySelector", selector, returns=JavaScriptObject
        )
        return JavaScriptNullable(
            self._context, value.as_javascript(), Element
        ).unwrap()

    def create_element(self, tag_name: String) -> Element:
        return self.call_method("createElement", tag_name, returns=Element)

    def alert(self, message: JavaScriptValue) -> None:
        """Convenience spelling from the example; alert belongs to window."""
        self._context.window.alert(message)


class Window(EventTarget):
    def alert(self, message: JavaScriptValue) -> None:
        self.call_method("alert", message, returns=JavaScriptUndefined)

    def confirm(self, message: String) -> JavaScriptBoolean:
        return self.call_method("confirm", message, returns=JavaScriptBoolean)

    def prompt(self, message: String) -> JavaScriptNullable[JavaScriptString]:
        value = self.call_method("prompt", message, returns=JavaScriptObject)
        return JavaScriptNullable(
            self._context, value.as_javascript(), JavaScriptString
        )

    def set_timeout(
        self,
        callback: JavaScriptFunction[JavaScriptHandle[object]],
        delay: Number = 0,
    ) -> JavaScriptNumber:
        return self.call_method(
            "setTimeout", callback, delay, returns=JavaScriptNumber
        )

    def clear_timeout(self, timeout: Number) -> None:
        self.call_method("clearTimeout", timeout, returns=JavaScriptUndefined)


class Console(JavaScriptObject):
    def log(self, *values: JavaScriptValue) -> None:
        self.call_method("log", *values, returns=JavaScriptUndefined)

    def warn(self, *values: JavaScriptValue) -> None:
        self.call_method("warn", *values, returns=JavaScriptUndefined)

    def error(self, *values: JavaScriptValue) -> None:
        self.call_method("error", *values, returns=JavaScriptUndefined)
