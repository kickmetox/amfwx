"""AMFWX-native JUCE interpretation (small subset)."""

from __future__ import annotations

from ..canvas import Rect
from ..quick import Stack
from ..widgets import Button, CheckBox, ComboBox, Label, LineEdit, Slider
from ..window import Window


class Colour:
    def __init__(self, r=0, g=0, b=0, a=255):
        self.rgba = (int(r), int(g), int(b), int(a))

    @classmethod
    def fromRGB(cls, r, g, b):
        return cls(r, g, b)

    def __repr__(self):
        return f"Colour{self.rgba}"


class Component:
    def __init__(self, name=""):
        self.name = name
        self.widget = None
        self.children = []
        self.visible = True

    def setBounds(self, x, y, width, height):
        if self.widget is not None:
            self.widget.arrange(Rect(int(x), int(y), int(width), int(height)))
        return self

    def getBounds(self):
        rect = self.widget.rect if self.widget is not None else Rect(0, 0, 0, 0)
        return (rect.x, rect.y, rect.w, rect.h)

    def addAndMakeVisible(self, child):
        self.children.append(child)
        if self.widget is not None and child.widget is not None:
            self.widget.add(child.widget)
        return child

    def setVisible(self, visible):
        self.visible = bool(visible)
        if self.widget is not None:
            self.widget.visible = self.visible
        return self

    def resized(self):
        return self

    def paint(self, _graphics):
        return self


class DocumentWindow(Component):
    def __init__(self, name="JUCE", width=800, height=600):
        super().__init__(name)
        self.window = Window(str(name), int(width), int(height))
        self.widget = self.window.root
        self.content = None

    def setContentOwned(self, component, _resize=True):
        self.content = component
        self.addAndMakeVisible(component)
        return self

    def centreWithSize(self, width, height):
        self.window.width = int(width)
        self.window.height = int(height)
        return self

    def setVisible(self, visible):
        super().setVisible(visible)
        return self

    def closeButtonPressed(self):
        self.window.close()


class Label(Component):
    def __init__(self, name="", text=""):
        super().__init__(name)
        self.widget = __import__("amfwx").Label(str(text))

    def setText(self, text, _notify=True):
        self.widget.text = str(text)

    def getText(self):
        return self.widget.text


class TextButton(Component):
    def __init__(self, name="", text=""):
        super().__init__(name)
        self._on_click = None
        self.widget = Button(str(text), on_click=self._clicked)

    def _clicked(self):
        if self._on_click is not None:
            self._on_click()

    def setButtonText(self, text):
        self.widget.text = str(text)

    def onClick(self, callback):
        self._on_click = callback

    def triggerClick(self):
        self.widget.activate()


class TextEditor(Component):
    def __init__(self, name=""):
        super().__init__(name)
        self.widget = LineEdit("")

    def setText(self, text):
        self.widget.set_text(str(text))

    def getText(self):
        return self.widget.text()


class Slider(Component):
    def __init__(self, name=""):
        super().__init__(name)
        self.widget = __import__("amfwx").widgets.Slider(0, 100, 0)

    def setRange(self, minimum, maximum):
        self.widget.minimum = int(minimum)
        self.widget.maximum = int(maximum)

    def setValue(self, value):
        self.widget.set_value(int(value))

    def getValue(self):
        return float(self.widget.value())


class ComboBox(Component):
    def __init__(self, name=""):
        super().__init__(name)
        self.widget = __import__("amfwx").widgets.ComboBox([])

    def addItem(self, text, item_id=None):
        self.widget.items.append(str(text))

    def setSelectedItemIndex(self, index):
        self.widget.current = int(index)

    def getSelectedItemIndex(self):
        return int(getattr(self.widget, "current", 0))


class ToggleButton(Component):
    def __init__(self, name="", text=""):
        super().__init__(name)
        self.widget = __import__("amfwx").CheckBox(str(text))

    def setToggleState(self, state, _notify=True):
        self.widget.checked = bool(state)

    def getToggleState(self):
        return bool(self.widget.checked)


class ResizableWindow(DocumentWindow):
    pass
