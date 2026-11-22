"""Minimal visual form designer for AMFWX."""

from __future__ import annotations

import json
from pathlib import Path

from .canvas import Rect
from .widgets import (Button, CheckBox, ComboBox, Label, LineEdit, Panel,
                      ProgressBar, Slider, Widget)
from .textedit import TextEdit
from .window import Window
from .text import draw_text


KINDS = ("label", "button", "line_edit", "text_edit", "checkbox",
         "slider", "combo", "progress")


class DesignerItem:
    def __init__(self, kind, text="", x=20, y=20, width=160, height=32):
        self.kind = str(kind)
        self.text = str(text)
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def to_dict(self):
        return {"kind": self.kind, "text": self.text, "x": self.x,
                "y": self.y, "width": self.width, "height": self.height}

    @classmethod
    def from_dict(cls, data):
        return cls(data.get("kind", "label"), data.get("text", ""),
                   data.get("x", 20), data.get("y", 20),
                   data.get("width", 160), data.get("height", 32))


class DesignerDocument:
    def __init__(self, title="Formular", items=None):
        self.title = str(title)
        self.items = list(items or [])
        self.selected = -1
        self._undo = []
        self._redo = []

    def _snapshot(self):
        return [DesignerItem(item.kind, item.text, item.x, item.y,
                             item.width, item.height) for item in self.items]

    def _record(self):
        self._undo.append(self._snapshot())
        if len(self._undo) > 60:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self):
        if not self._undo:
            return False
        self._redo.append(self._snapshot())
        self.items = self._undo.pop()
        self.selected = min(self.selected, len(self.items) - 1)
        return True

    def redo(self):
        if not self._redo:
            return False
        self._undo.append(self._snapshot())
        self.items = self._redo.pop()
        self.selected = min(self.selected, len(self.items) - 1)
        return True

    def add(self, kind, text="", x=20, y=20, width=160, height=32):
        self._record()
        item = DesignerItem(kind, text, x, y, width, height)
        self.items.append(item)
        self.selected = len(self.items) - 1
        return item

    def remove(self, index=None):
        index = self.selected if index is None else int(index)
        if 0 <= index < len(self.items):
            self._record()
            del self.items[index]
            self.selected = min(index, len(self.items) - 1)
            return True
        return False

    def select(self, index):
        self.selected = max(-1, min(len(self.items) - 1, int(index)))
        return self.selected

    def move(self, index, x, y):
        if 0 <= index < len(self.items):
            self._record()
            self.items[index].x = int(x)
            self.items[index].y = int(y)
            return True
        return False

    def resize(self, index, width, height):
        if 0 <= index < len(self.items):
            self._record()
            self.items[index].width = max(8, int(width))
            self.items[index].height = max(8, int(height))
            return True
        return False

    def to_dict(self):
        return {"title": self.title,
                "items": [item.to_dict() for item in self.items]}

    @classmethod
    def from_dict(cls, data):
        return cls(data.get("title", "Formular"),
                   [DesignerItem.from_dict(item)
                    for item in data.get("items", [])])

    def key_down(self, key, modifiers=0):
        if key == 90 and modifiers & 2:
            self.document.undo()
        elif key == 89 and modifiers & 2:
            self.document.redo()
        elif key == 46:
            self.document.remove()
        return super().key_down(key, modifiers)

    def save(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2,
                                         ensure_ascii=False),
                              encoding="utf-8")
        return self

    @classmethod
    def load(cls, path):
        return cls.from_dict(json.loads(Path(path).read_text(
            encoding="utf-8")))

    def generate_code(self):
        lines = ["from amfwx import (Button, CheckBox, ComboBox, Label,",
                 "                     LineEdit, ProgressBar, Slider, TextEdit,",
                 "                     Rect, Window)", "",
                 f"window = Window({self.title!r}, 900, 600)"]
        for item in self.items:
            kind = item.kind
            text = repr(item.text)
            if kind == "label":
                statement = f"Label({text})"
            elif kind == "button":
                statement = f"Button({text})"
            elif kind == "line_edit":
                statement = f"LineEdit({text})"
            elif kind == "text_edit":
                statement = f"TextEdit({text})"
            elif kind == "checkbox":
                statement = f"CheckBox({text})"
            elif kind == "slider":
                statement = "Slider(0, 100, 0)"
            elif kind == "combo":
                statement = "ComboBox(['A', 'B'])"
            elif kind == "progress":
                statement = "ProgressBar(0)"
            else:
                statement = "Label('')"
            name = f"widget_{len(lines)}"
            lines.append(f"{name} = {statement}")
            lines.append(f"{name}.arrange(Rect({item.x}, {item.y}, "
                         f"{item.width}, {item.height}))")
            lines.append(f"window.root.add({name})")
        lines.append("window.run()")
        return "\n".join(lines) + "\n"


class DesignerCanvas(Widget):
    def __init__(self, document):
        super().__init__()
        self.document = document
        self._drag = None
        self._resize = None

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface)
        step = 16
        x = self.rect.x
        while x < self.rect.right:
            canvas.line(x, self.rect.y, x, self.rect.bottom,
                        theme.border.with_alpha(60))
            x += step
        y = self.rect.y
        while y < self.rect.bottom:
            canvas.line(self.rect.x, y, self.rect.right, y,
                        theme.border.with_alpha(60))
            y += step
        for index, item in enumerate(self.document.items):
            rect = Rect(self.rect.x + item.x, self.rect.y + item.y,
                        item.width, item.height)
            canvas.fill_rect(rect, theme.surface_alt)
            color = theme.accent if index == self.document.selected else theme.border
            if index == self.document.selected:
                canvas.fill_rect(rect, theme.accent.with_alpha(40))
            canvas.fill_rect(Rect(rect.x, rect.y, rect.w, 1), color)
            canvas.fill_rect(Rect(rect.x, rect.bottom - 1, rect.w, 1), color)
            canvas.fill_rect(Rect(rect.x, rect.y, 1, rect.h), color)
            canvas.fill_rect(Rect(rect.right - 1, rect.y, 1, rect.h), color)
            label = item.text or item.kind
            draw_text(canvas, label, rect.x + 4, rect.y + 4, theme.text, 1)

    def mouse_down(self, x, y, button="left"):
        local_x, local_y = x - self.rect.x, y - self.rect.y
        for index, item in enumerate(self.document.items):
            if (item.x <= local_x < item.x + item.width and
                    item.y <= local_y < item.y + item.height):
                self.document.select(index)
                if (local_x >= item.x + item.width - 10 and
                        local_y >= item.y + item.height - 10):
                    self._resize = (index, item.width, item.height,
                                    local_x, local_y)
                else:
                    self._drag = (index, local_x - item.x, local_y - item.y)
                return
        self.document.select(-1)
        self._drag = None

    def mouse_move(self, x, y):
        if self._resize is not None:
            index, width, height, start_x, start_y = self._resize
            self.document.resize(index, width + (x - self.rect.x - start_x),
                                 height + (y - self.rect.y - start_y))
            self._resize = (index, width, height, start_x, start_y)
            return
        if self._drag is None:
            return
        index, offset_x, offset_y = self._drag
        self.document.move(index, x - self.rect.x - offset_x,
                           y - self.rect.y - offset_y)

    def mouse_up(self, x, y, button="left"):
        self._drag = None
        self._resize = None


class DesignerWindow(Window):
    def __init__(self, document=None):
        super().__init__("AMFWX Designer", 900, 600)
        self.document = document or DesignerDocument()
        self.palette = Panel()
        self.canvas = DesignerCanvas(self.document)
        self.property_panel = Panel()
        self.root.add(self.palette)
        self.root.add(self.canvas)
        self.root.add(self.property_panel)
        self.palette.arrange(Rect(0, 0, 160, 600))
        self.canvas.arrange(Rect(160, 0, 520, 600))
        self.property_panel.arrange(Rect(680, 0, 220, 600))
        for index, kind in enumerate(KINDS):
            button = Button(kind)
            button.parent = self.palette
            button.arrange(Rect(8, 8 + index * 36, 144, 30))
            button.on_click = (lambda k=kind: self.document.add(k, k))
            self.palette.children.append(button)

    def key_down(self, key, modifiers=0):
        if key == 90 and modifiers & 2:
            self.document.undo()
        elif key == 89 and modifiers & 2:
            self.document.redo()
        elif key == 46:
            self.document.remove()
        return super().key_down(key, modifiers)

    def save(self, path):
        return self.document.save(path)

    def load(self, path):
        self.document = DesignerDocument.load(path)
        self.canvas.document = self.document
        return self

    def generate_code(self):
        return self.document.generate_code()
