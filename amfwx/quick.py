"""Minimal declarative UI layer for AMFWX.

This is intentionally small: State, a builder function and a QuickView that
rebuilds its widget tree when state changes.
"""

from __future__ import annotations

from .widgets import BoxLayout, Button, Label, LineEdit
from .window import Window


class State:
    def __init__(self, value=None):
        self._value = value
        self._listeners = []

    @property
    def value(self):
        return self._value

    def set(self, value):
        if value == self._value:
            return
        self._value = value
        self._notify()

    def update(self, function):
        self.set(function(self._value))

    def subscribe(self, callback):
        self._listeners.append(callback)
        return callback

    def unsubscribe(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self):
        for callback in list(self._listeners):
            callback(self._value)


def Text(value):
    if callable(value):
        value = value()
    return Label(str(value))


def Button_(text, on_click=None):
    if callable(text):
        text = text()
    return Button(str(text), on_click=on_click)


def TextField(value="", on_change=None):
    edit = LineEdit(str(value))
    if on_change is not None:
        edit.on_change = on_change
    return edit


class QuickView(Window):
    def __init__(self, title, build, width=640, height=480, state=None):
        super().__init__(title, width, height)
        self.build = build
        self.state = state
        self.layout = BoxLayout("vertical", spacing=8, padding=12)
        self.root.layout = self.layout
        self._listener = None
        if state is not None:
            self._listener = lambda _value: self.refresh()
            state.subscribe(self._listener)
        self.refresh()

    def refresh(self):
        self.root.children.clear()
        self.layout.items.clear()
        widgets = self.build(self.state.value if self.state else None)
        if widgets is None:
            widgets = []
        if not isinstance(widgets, (list, tuple)):
            widgets = [widgets]
        for widget in widgets:
            self.root.add(widget)
            self.layout.add(widget)
        self._layout_root()
        self.invalidate()
        return self

    def dispose(self):
        if self.state is not None and self._listener is not None:
            self.state.unsubscribe(self._listener)
            self._listener = None
        self.close()
