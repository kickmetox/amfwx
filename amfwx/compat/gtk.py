"""AMFWX-native GTK interpretation (small subset)."""

from __future__ import annotations

from ..canvas import Rect
from ..quick import Stack
from ..widgets import (BoxLayout, Button as _Button, CheckBox as _CheckBox,
                       Label as _Label, LineEdit as _LineEdit,
                       Panel as _Panel, ProgressBar as _ProgressBar,
                       Slider as _Slider)
from ..window import Window


class Orientation:
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class Application:
    def __init__(self, application_id="", *args, **kwargs):
        self.application_id = application_id
        self.window = None

    def run(self, argv=None):
        if self.window is not None:
            return self.window.window.run()
        return 0

    def quit(self):
        if self.window is not None:
            self.window.window.close()


class ApplicationWindow:
    def __init__(self, application=None, title="GTK", width=800, height=600):
        self.application = application
        self.window = Window(str(title), int(width), int(height))
        self.widget = self.window.root
        if application is not None:
            application.window = self

    def set_child(self, child):
        target = getattr(child, "widget", child)
        target.parent = self.widget
        self.widget.add(target)
        return self

    def present(self):
        self.widget.visible = True
        return self

    def close(self):
        self.window.close()


class Box:
    def __init__(self, orientation=Orientation.VERTICAL, spacing=6, **kwargs):
        self.widget = Stack(orientation, spacing=spacing, padding=6)

    def append(self, child):
        target = getattr(child, "widget", child)
        self.widget.add(target)
        return self

    def set_spacing(self, spacing):
        self.widget.layout.spacing = int(spacing)
        return self


class Grid:
    def __init__(self, spacing=6):
        self.widget = _Panel()
        self.spacing = spacing
        self._row = 0

    def attach(self, child, column=0, row=0, width=1, height=1):
        target = getattr(child, "widget", child)
        self.widget.add(target)
        target.arrange(Rect(8 + column * 160, 8 + row * 40, 150, 32))
        return self


class Label:
    def __init__(self, label=""):
        self.widget = _Label(str(label))

    def set_label(self, text):
        self.widget.text = str(text)

    def get_label(self):
        return self.widget.text


class Button:
    def __init__(self, label=""):
        self.widget = __import__("amfwx").Button(str(label))
        self._handlers = {}

    def connect(self, signal, callback):
        self._handlers[signal] = callback
        if signal == "clicked":
            self.widget.on_click = lambda: callback(self)
        return self

    def set_label(self, text):
        self.widget.text = str(text)


class Entry:
    def __init__(self, text=""):
        self.widget = _LineEdit(str(text))

    def get_text(self):
        return self.widget.text()

    def set_text(self, text):
        self.widget.set_text(str(text))


class CheckButton:
    def __init__(self, label=""):
        self.widget = __import__("amfwx").CheckBox(str(label))

    def get_active(self):
        return bool(self.widget.checked)

    def set_active(self, active):
        self.widget.checked = bool(active)


class Switch:
    def __init__(self):
        self.widget = __import__("amfwx").CheckBox("")

    def get_active(self):
        return bool(self.widget.checked)

    def set_active(self, active):
        self.widget.checked = bool(active)


class Scale:
    def __init__(self, orientation=Orientation.HORIZONTAL):
        self.widget = _Slider(0, 100, 0)

    def get_value(self):
        return float(self.widget.value())

    def set_value(self, value):
        self.widget.set_value(int(value))


class ProgressBar:
    def __init__(self):
        self.widget = _ProgressBar(0, 100)

    def set_fraction(self, value):
        self.widget.set_value(int(max(0.0, min(1.0, float(value))) * 100))

    def pulse(self):
        return self


class Separator:
    def __init__(self, orientation=Orientation.HORIZONTAL):
        self.widget = _Panel()


class HeaderBar:
    def __init__(self):
        self.title = ""

    def set_title(self, title):
        self.title = str(title)
