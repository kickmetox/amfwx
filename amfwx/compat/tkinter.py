"""AMFWX-native Tkinter interpretation.

This is not Tcl/Tk. It maps a small Tkinter API surface onto AMFWX widgets.
"""

from __future__ import annotations

from ..canvas import Rect
from ..advanced import TabView
from ..quick import Stack
from ..widgets import (BoxLayout, Button, CheckBox, ComboBox, Label, LineEdit,
                       Panel, ProgressBar, TreeItem, TreeView)
from ..window import Window


class Variable:
    def __init__(self, value=None):
        self._value = value
        self._callbacks = []

    def get(self):
        return self._value

    def set(self, value):
        self._value = value
        for callback in list(self._callbacks):
            callback()

    def trace_add(self, mode, callback):
        self._callbacks.append(callback)
        return callback

    def trace(self, mode, callback):
        return self.trace_add(mode, callback)


class StringVar(Variable):
    def __init__(self, value=""):
        super().__init__(str(value))

    def set(self, value):
        super().set(str(value))


class IntVar(Variable):
    def __init__(self, value=0):
        super().__init__(int(value))

    def set(self, value):
        super().set(int(value))


class DoubleVar(Variable):
    def __init__(self, value=0.0):
        super().__init__(float(value))

    def set(self, value):
        super().set(float(value))


class BooleanVar(Variable):
    def __init__(self, value=False):
        super().__init__(bool(value))

    def set(self, value):
        super().set(bool(value))


class _Base:
    def __init__(self, master=None):
        self.master = master
        self.widget = None

    def pack(self, side="top", fill="none", expand=False, padx=0, pady=0):
        parent = self.master
        layout = getattr(parent, "layout", None)
        if layout is None:
            raise RuntimeError("Parent hat kein Layout")
        self.widget.parent = parent.widget if hasattr(parent, "widget") else parent
        layout.add(self.widget)
        return self

    def grid(self, row=0, column=0, padx=0, pady=0, sticky="nsew"):
        parent = self.master
        if isinstance(parent, Tk):
            x, y = column * 180 + 12, row * 40 + 12
        else:
            x, y = column * 160 + 4, row * 36 + 4
        target = parent.widget if hasattr(parent, "widget") else parent
        if hasattr(target, "add"):
            target.add(self.widget)
        self.widget.arrange(Rect(x, y, self.widget.size_hint()[0],
                                 self.widget.size_hint()[1]))
        return self

    def place(self, x=0, y=0, width=None, height=None):
        width = width or self.widget.size_hint()[0]
        height = height or self.widget.size_hint()[1]
        parent = self.master
        target = parent.widget if hasattr(parent, "widget") else parent
        if hasattr(target, "add"):
            target.add(self.widget)
        self.widget.arrange(Rect(int(x), int(y), int(width), int(height)))
        return self

    def configure(self, **kwargs):
        if "text" in kwargs and hasattr(self.widget, "text"):
            self.widget.text = kwargs["text"]
        if "state" in kwargs and hasattr(self.widget, "enabled"):
            self.widget.enabled = kwargs["state"] != "disabled"
        return self

    config = configure

    def bind(self, event, callback):
        if event in ("<Button-1>", "<ButtonRelease-1>"):
            self.widget.on_click = lambda: callback(None)
        return self

    def destroy(self):
        if self.widget is not None:
            self.widget.visible = False


class Tk:
    def __init__(self, title="Tk", width=800, height=600):
        self.window = Window(title, width, height)
        self.widget = self.window.root
        self.layout = BoxLayout("vertical", spacing=8, padding=12)
        self.window.root.layout = self.layout
        self.children = []

    def title(self, text=None):
        if text is not None:
            self.window.title = str(text)
        return self.window.title

    def geometry(self, value=None):
        if value:
            parts = str(value).lower().split("x")
            if len(parts) == 2:
                self.window.width = int(parts[0])
                self.window.height = int(parts[1])
        return f"{self.window.width}x{self.window.height}"

    def mainloop(self):
        return self.window.run()

    def update(self):
        self.window.process_events(40)

    def destroy(self):
        self.window.close()
        self.window.process_events(40)

    def after(self, _delay, callback):
        callback()
        return "after#0"


class Frame(_Base):
    def __init__(self, master=None, **kwargs):
        super().__init__(master)
        self.widget = Stack("vertical", spacing=6, padding=6)
        self.layout = self.widget.layout


class Label(_Base):
    def __init__(self, master=None, text="", **kwargs):
        super().__init__(master)
        self.widget = __import__("amfwx").Label(str(text))


class Button(_Base):
    def __init__(self, master=None, text="", command=None, **kwargs):
        super().__init__(master)
        self.widget = __import__("amfwx").Button(str(text), on_click=command)


class Entry(_Base):
    def __init__(self, master=None, textvariable=None, **kwargs):
        super().__init__(master)
        self.variable = textvariable
        self._syncing = False
        self.widget = LineEdit(str(textvariable.get()) if textvariable else "")
        if textvariable is not None:
            def from_widget(value):
                if self._syncing:
                    return
                self._syncing = True
                textvariable.set(value)
                self._syncing = False
            def from_variable():
                if self._syncing:
                    return
                self._syncing = True
                self.widget.set_text(textvariable.get())
                self._syncing = False
            self.widget.on_change = from_widget
            textvariable.trace_add("write", from_variable)

    def get(self):
        return self.widget.text()

    def insert(self, index, text):
        self.widget.set_text(self.widget.text() + str(text))

    def delete(self, first, last=None):
        self.widget.set_text("")


class Checkbutton(_Base):
    def __init__(self, master=None, text="", variable=None, command=None,
                 **kwargs):
        super().__init__(master)
        self.variable = variable
        self.command = command
        self.widget = __import__("amfwx").CheckBox(
            str(text), bool(variable.get()) if variable else False,
            on_change=self._changed)

    def _changed(self, value):
        if self.variable is not None:
            self.variable.set(value)
        if self.command is not None:
            self.command()

    def invoke(self):
        self.widget.toggle()
        return self


class Canvas(_Base):
    def __init__(self, master=None, width=300, height=200, **kwargs):
        super().__init__(master)
        self.widget = Panel()
        self.width = int(width)
        self.height = int(height)
        self.widget.size_hint = lambda: (self.width, self.height)


class Menu:
    def __init__(self, master=None):
        self.master = master
        self.items = []

    def add_command(self, label="", command=None):
        self.items.append((label, command))
        return self


class _MessageBox:
    def showinfo(self, title="Info", message=""):
        from ..dialog import MessageBox
        MessageBox.show(None, message, title)

    def showwarning(self, title="Warnung", message=""):
        self.showinfo(title, message)

    def showerror(self, title="Fehler", message=""):
        self.showinfo(title, message)


messagebox = _MessageBox()


class Notebook(_Base):
    def __init__(self, master=None, **kwargs):
        super().__init__(master)
        self.widget = TabView()

    def add(self, child, text="Tab"):
        self.widget.add_tab(str(text), child.widget)
        return self

    def select(self, index):
        self.widget.active = int(index)
        self.widget.arrange(self.widget.rect)
        return self

    def index(self, child):
        for index, (_title, page) in enumerate(self.widget.tabs):
            if page is child.widget:
                return index
        return -1


class Treeview(_Base):
    def __init__(self, master=None, columns=(), **kwargs):
        super().__init__(master)
        self.widget = TreeView([])
        self.columns = tuple(columns)

    def insert(self, parent="", index="end", text="", values=()):
        item = TreeItem(str(text))
        if parent:
            target = self._find(parent)
            if target is not None:
                target.children.append(item)
        else:
            self.widget.items.append(item)
        return item

    def _find(self, wanted):
        stack = list(self.widget.items)
        while stack:
            item = stack.pop()
            if item is wanted or item.label == wanted:
                return item
            stack.extend(item.children)
        return None

    def delete(self, item):
        for collection in [self.widget.items] + [i.children for i in
                                                 self._all()]:
            if item in collection:
                collection.remove(item)
                return True
        return False

    def _all(self):
        result = []
        stack = list(self.widget.items)
        while stack:
            item = stack.pop()
            result.append(item)
            stack.extend(item.children)
        return result

    def selection(self):
        return [self.widget.selected] if self.widget.selected else []


class Progressbar(_Base):
    def __init__(self, master=None, value=0, maximum=100, **kwargs):
        super().__init__(master)
        self.widget = ProgressBar(int(value), int(maximum))

    def configure(self, **kwargs):
        if "value" in kwargs:
            self.widget.set_value(kwargs["value"])
        return self

    config = configure


class Combobox(_Base):
    def __init__(self, master=None, values=(), **kwargs):
        super().__init__(master)
        self.widget = ComboBox(list(values or []))

    def get(self):
        return self.widget.current_text()

    def set(self, value):
        value = str(value)
        if value not in self.widget.items:
            self.widget.items.append(value)
        self.widget.set_current_index(self.widget.items.index(value))
        return self

    def current(self, index=None):
        if index is None:
            return int(self.widget.current_index)
        self.widget.set_current_index(int(index))
        return self


class _TTK:
    Notebook = Notebook
    Treeview = Treeview
    Progressbar = Progressbar
    Combobox = Combobox


ttk = _TTK()
