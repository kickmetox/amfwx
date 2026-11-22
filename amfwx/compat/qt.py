"""AMFWX-native Qt/PySide interpretation (small subset)."""

from __future__ import annotations

from ..quick import Stack
from ..textedit import TextEdit
from ..widgets import (BoxLayout, Button as _Button, CheckBox as _CheckBox,
                       ComboBox as _ComboBox, Label as _Label,
                       LineEdit as _LineEdit, ProgressBar as _ProgressBar,
                       Slider as _Slider)
from ..window import Window


class QApplication:
    def __init__(self, argv=None):
        self.argv = list(argv or [])
        self.window = None

    def exec(self):
        if self.window is not None:
            return self.window.window.run()
        return 0

    exec_ = exec

    def quit(self):
        if self.window is not None:
            self.window.window.close()


class QWidget:
    def __init__(self, parent=None):
        self.parent = parent
        self.widget = Stack("vertical", spacing=4, padding=4)
        if parent is not None:
            parent.widget.add(self.widget)

    def setLayout(self, layout):
        self.widget.layout = layout.build()
        return self

    def show(self):
        self.widget.visible = True
        return self

    def hide(self):
        self.widget.visible = False
        return self

    def setWindowTitle(self, title):
        if hasattr(self, "window"):
            self.window.title = str(title)
        return self


class QMainWindow:
    def __init__(self, parent=None, title="Qt", width=800, height=600):
        self.window = Window(str(title), int(width), int(height))
        self.widget = self.window.root
        self.central = None

    def setCentralWidget(self, widget):
        self.central = widget
        self.widget.add(widget.widget)
        return self

    def show(self):
        self.widget.visible = True
        return self

    def close(self):
        self.window.close()


class QVBoxLayout:
    def __init__(self, parent=None):
        self.orientation = "vertical"
        self.items = []
        if parent is not None:
            parent.setLayout(self)

    def addWidget(self, widget):
        self.items.append(widget)
        return self

    def addStretch(self, _value=0):
        return self

    def build(self):
        layout = BoxLayout(self.orientation, spacing=4, padding=4)
        for widget in self.items:
            layout.add(widget.widget)
        return layout


class QHBoxLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.orientation = "horizontal"


class QLabel:
    def __init__(self, text="", parent=None):
        self.widget = _Label(str(text))
        if parent is not None:
            parent.widget.add(self.widget)

    def setText(self, text):
        self.widget.text = str(text)

    def text(self):
        return self.widget.text


class _Signal:
    def __init__(self):
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)

    def emit(self, *args):
        for callback in list(self._callbacks):
            callback(*args)


class QPushButton:
    def __init__(self, text="", parent=None):
        self.clicked = _Signal()
        self.widget = _Button(str(text), on_click=self.clicked.emit)
        if parent is not None:
            parent.widget.add(self.widget)

    def setText(self, text):
        self.widget.text = str(text)

    def click(self):
        self.widget.activate()


class QLineEdit:
    def __init__(self, text="", parent=None):
        self.widget = _LineEdit(str(text))
        if parent is not None:
            parent.widget.add(self.widget)

    def text(self):
        return self.widget.text()

    def setText(self, text):
        self.widget.set_text(str(text))


class QCheckBox:
    def __init__(self, text="", parent=None):
        self.widget = _CheckBox(str(text))
        if parent is not None:
            parent.widget.add(self.widget)

    def isChecked(self):
        return bool(self.widget.checked)

    def setChecked(self, checked):
        self.widget.checked = bool(checked)


class QSlider:
    def __init__(self, orientation=None, parent=None):
        self.widget = _Slider(0, 100, 0)
        if parent is not None:
            parent.widget.add(self.widget)

    def setValue(self, value):
        self.widget.set_value(int(value))

    def value(self):
        return int(self.widget.value())


class QComboBox:
    def __init__(self, parent=None):
        self.widget = _ComboBox([])
        if parent is not None:
            parent.widget.add(self.widget)

    def addItem(self, text):
        self.widget.items.append(str(text))

    def setCurrentIndex(self, index):
        self.widget.current = int(index)

    def currentIndex(self):
        return int(getattr(self.widget, "current", 0))


class QProgressBar:
    def __init__(self, parent=None):
        self.widget = _ProgressBar(0, 100)
        if parent is not None:
            parent.widget.add(self.widget)

    def setValue(self, value):
        self.widget.set_value(int(value))


class QTextEdit:
    def __init__(self, parent=None):
        self.widget = TextEdit("")
        if parent is not None:
            parent.widget.add(self.widget)

    def setPlainText(self, text):
        self.widget.set_text(str(text))

    def toPlainText(self):
        return self.widget.text()
