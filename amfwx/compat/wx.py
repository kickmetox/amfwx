"""AMFWX-native wxWidgets interpretation (small subset)."""

from __future__ import annotations

from ..quick import Stack
from ..widgets import BoxLayout, Button, CheckBox, ComboBox, Label, LineEdit, ProgressBar
from ..window import Window

VERTICAL = "vertical"
HORIZONTAL = "horizontal"
ALL = 1
EXPAND = 2
ID_ANY = -1
EVT_BUTTON = "button"
EVT_TEXT = "text"


class App:
    def __init__(self, *args, **kwargs):
        self.frame = None

    def MainLoop(self):
        if self.frame is not None:
            return self.frame.window.run()
        return 0

    def ExitMainLoop(self):
        if self.frame is not None:
            self.frame.window.close()


class _Widget:
    def __init__(self, parent=None):
        self.parent = parent
        self.widget = None
        self._handlers = {}

    def Bind(self, event, callback):
        self._handlers[event] = callback
        if event == EVT_BUTTON and hasattr(self.widget, "on_click"):
            self.widget.on_click = lambda: callback(None)
        return self

    def Show(self, show=True):
        if self.widget is not None:
            self.widget.visible = bool(show)
        return self

    def Enable(self, enable=True):
        if self.widget is not None:
            self.widget.enabled = bool(enable)
        return self

    def SetToolTip(self, text):
        if self.widget is not None:
            self.widget.tooltip = str(text)
        return self


class Frame(_Widget):
    def __init__(self, parent=None, title="wx", size=(800, 600)):
        super().__init__(parent)
        self.window = Window(str(title), int(size[0]), int(size[1]))
        self.widget = self.window.root
        self.sizer = None
        if isinstance(parent, App):
            parent.frame = self

    def SetSizer(self, sizer):
        self.sizer = sizer
        self.widget.layout = sizer.build()
        return self

    def Layout(self):
        self.window._layout_root()
        return self

    def Show(self, show=True):
        return super().Show(show)

    def Destroy(self):
        self.window.close()
        self.window.process_events(40)


class Panel(_Widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = Stack("vertical", spacing=4, padding=4)
        self.sizer = None
        if isinstance(parent, Frame):
            parent.widget.add(self.widget)

    def SetSizer(self, sizer):
        self.sizer = sizer
        self.widget.layout = sizer.build()
        return self


class BoxSizer:
    def __init__(self, orientation=VERTICAL):
        self.orientation = orientation
        self.items = []

    def Add(self, widget, proportion=0, flag=0, border=0):
        self.items.append((widget, proportion))
        return self

    def build(self):
        layout = BoxLayout(self.orientation, spacing=4, padding=4)
        for widget, proportion in self.items:
            target = getattr(widget, "widget", widget)
            layout.add(target, stretch=int(proportion))
        return layout


class StaticText(_Widget):
    def __init__(self, parent=None, label=""):
        super().__init__(parent)
        self.widget = Label(str(label))
        if isinstance(parent, (Panel, Frame)):
            parent.widget.add(self.widget)

    def SetLabel(self, label):
        self.widget.text = str(label)


class Button(_Widget):
    def __init__(self, parent=None, label=""):
        super().__init__(parent)
        self.widget = __import__("amfwx").Button(str(label))
        if isinstance(parent, (Panel, Frame)):
            parent.widget.add(self.widget)

    def SetLabel(self, label):
        self.widget.text = str(label)


class TextCtrl(_Widget):
    def __init__(self, parent=None, value=""):
        super().__init__(parent)
        self.widget = LineEdit(str(value))
        if isinstance(parent, (Panel, Frame)):
            parent.widget.add(self.widget)

    def GetValue(self):
        return self.widget.text()

    def SetValue(self, value):
        self.widget.set_text(str(value))


class CheckBox(_Widget):
    def __init__(self, parent=None, label=""):
        super().__init__(parent)
        self.widget = __import__("amfwx").CheckBox(str(label))
        if isinstance(parent, (Panel, Frame)):
            parent.widget.add(self.widget)

    def GetValue(self):
        return bool(self.widget.checked)

    def SetValue(self, value):
        self.widget.checked = bool(value)


class Gauge(_Widget):
    def __init__(self, parent=None, range=100):
        super().__init__(parent)
        self.widget = ProgressBar(0, range)
        if isinstance(parent, (Panel, Frame)):
            parent.widget.add(self.widget)

    def SetValue(self, value):
        self.widget.set_value(value)


class Choice(_Widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = ComboBox([])
        if isinstance(parent, (Panel, Frame)):
            parent.widget.add(self.widget)

    def Append(self, item):
        self.widget.items.append(str(item))
        return self

    def GetSelection(self):
        return int(getattr(self.widget, "current", 0))

    def SetSelection(self, index):
        self.widget.current = int(index)


class Menu:
    def __init__(self):
        self.items = []

    def Append(self, _id, label, help=""):
        self.items.append((label, _id))
        return self


class MenuBar:
    def __init__(self):
        self.menus = []

    def Append(self, menu, label):
        self.menus.append((label, menu))
        return self


class StatusBar:
    def __init__(self, parent=None):
        self.parent = parent
        self.text = ""

    def SetStatusText(self, text):
        self.text = str(text)
