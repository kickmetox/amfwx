"""Accessibility provider model for AMFWX.

This is the provider architecture below UIA/MSAA. It builds a stable
accessibility tree from widgets, independent of the native proxy windows.
"""

from __future__ import annotations

from .widgets import Widget


ROLE_WINDOW = "window"
ROLE_BUTTON = "button"
ROLE_CHECKBOX = "checkbox"
ROLE_EDIT = "edit"
ROLE_TEXT = "text"
ROLE_LIST = "list"
ROLE_LIST_ITEM = "listitem"
ROLE_TREE = "tree"
ROLE_TREE_ITEM = "treeitem"
ROLE_SLIDER = "slider"
ROLE_COMBO = "combobox"
ROLE_TABLE = "table"
ROLE_PANEL = "panel"
ROLE_TAB = "tab"
ROLE_IMAGE = "image"
ROLE_UNKNOWN = "unknown"


class AccessibilityNode:
    def __init__(self, widget, role, name="", value="", children=None):
        self.widget = widget
        self.role = role
        self.name = str(name or "")
        self.value = value
        self.children = list(children or [])
        self.parent = None
        for child in self.children:
            child.parent = self

    @property
    def bounds(self):
        rect = getattr(self.widget, "rect", None)
        if rect is None:
            return (0, 0, 0, 0)
        return (int(rect.x), int(rect.y), int(rect.w), int(rect.h))

    @property
    def enabled(self):
        return bool(getattr(self.widget, "enabled", True))

    @property
    def focused(self):
        return bool(getattr(self.widget, "focused", False))

    @property
    def offscreen(self):
        return not bool(getattr(self.widget, "visible", True))

    @property
    def checked(self):
        return getattr(self.widget, "checked", None)

    def activate(self):
        activate = getattr(self.widget, "activate", None)
        if activate is not None:
            activate()
            return True
        toggle = getattr(self.widget, "toggle", None)
        if toggle is not None:
            toggle()
            return True
        return False

    def set_value(self, text):
        setter = getattr(self.widget, "set_text", None)
        if setter is not None:
            setter(text)
            return True
        return False

    def focus(self):
        window = getattr(self.widget, "window", lambda: None)()
        if window is not None:
            window.set_focus(self.widget)
            return True
        return False

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def __repr__(self):
        return (f"AccessibilityNode(role={self.role!r}, name={self.name!r}, "
                f"value={self.value!r})")


class AccessibilityTree:
    def __init__(self, window):
        self.window = window
        self.root = self._build()

    def _build(self):
        labels = {}
        for widget in self._widgets():
            target = getattr(widget, "label_for", None)
            if target is not None:
                labels[id(target)] = getattr(widget, "text", "")
        root = AccessibilityNode(self.window.root, ROLE_WINDOW,
                                 getattr(self.window, "title", ""))
        self._populate(root, labels)
        return root

    def _widgets(self):
        stack = list(getattr(self.window.root, "children", []))
        while stack:
            widget = stack.pop()
            yield widget
            stack.extend(getattr(widget, "children", []))

    def _populate(self, node, labels):
        for widget in getattr(node.widget, "children", []):
            if not getattr(widget, "visible", True):
                continue
            role = role_for(widget)
            name = accessible_name(widget, labels)
            value = accessible_value(widget, role)
            child = AccessibilityNode(widget, role, name, value)
            node.children.append(child)
            child.parent = node
            self._populate(child, labels)

    def find(self, widget):
        for node in self.root.walk():
            if node.widget is widget:
                return node
        return None

    def walk(self):
        return self.root.walk()


def role_for(widget):
    name = type(widget).__name__
    return {
        "Button": ROLE_BUTTON,
        "CheckBox": ROLE_CHECKBOX,
        "LineEdit": ROLE_EDIT,
        "TextEdit": ROLE_EDIT,
        "Label": ROLE_TEXT,
        "ListView": ROLE_LIST,
        "TreeView": ROLE_TREE,
        "TreeItem": ROLE_TREE_ITEM,
        "Slider": ROLE_SLIDER,
        "ComboBox": ROLE_COMBO,
        "TableView": ROLE_TABLE,
        "TabView": ROLE_TAB,
        "ImageView": ROLE_IMAGE,
        "Panel": ROLE_PANEL,
    }.get(name, ROLE_UNKNOWN)


def accessible_name(widget, labels=None):
    explicit = getattr(widget, "accessible_name", "")
    if explicit:
        return explicit
    if labels and id(widget) in labels:
        return labels[id(widget)]
    role = role_for(widget)
    text = getattr(widget, "text", "")
    if callable(text):
        text = text()
    if role in (ROLE_TEXT, ROLE_BUTTON, ROLE_CHECKBOX):
        return str(text or "")
    return ""


def accessible_value(widget, role=None):
    role = role or role_for(widget)
    if role == ROLE_EDIT:
        getter = getattr(widget, "text", "")
        return getter() if callable(getter) else str(getter or "")
    if role == ROLE_CHECKBOX:
        return "checked" if getattr(widget, "checked", False) else "unchecked"
    if role == ROLE_SLIDER:
        return str(getattr(widget, "value", ""))
    if role == ROLE_COMBO:
        getter = getattr(widget, "current_text", None)
        if getter is not None:
            return str(getter())
    return ""


class AccessibilityBridge:
    """Couple the provider tree to the native proxy windows."""

    def __init__(self, window):
        self.window = window

    def tree(self):
        return self.window.accessibility_tree()

    def sync(self):
        import ctypes
        user32 = ctypes.windll.user32
        user32.SendMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint,
                                        ctypes.c_size_t, ctypes.c_ssize_t]
        tree = self.tree()
        self.window._proxy_updating = True
        try:
            for node in tree.walk():
                handle = getattr(self.window, "_a11y_windows", {}).get(
                    id(node.widget))
                if not handle:
                    continue
                text = node.value if node.role == ROLE_EDIT else node.name
                if getattr(self.window, "_uia_native", None) and int(handle) in self.window._uia_native:
                    try:
                        from .uia_native import set_name as set_uia_name
                        old_name = getattr(self.window, "_a11y_names", {}).get(int(handle), "")
                        set_uia_name(handle, node.name)
                        if old_name != node.name:
                            try:
                                from .uia_native import notify_name
                                notify_name(handle, old_name, node.name)
                            except Exception:
                                pass
                            names = getattr(self.window, "_a11y_names", {})
                            names[int(handle)] = node.name
                            self.window._a11y_names = names
                        set_bounds = getattr(__import__("amfwx.uia_native", fromlist=["set_bounds"]), "set_bounds")
                        set_bounds(handle, node.bounds[0], node.bounds[1],
                                   max(1, node.bounds[2]), max(1, node.bounds[3]))
                    except Exception:
                        pass
                if text:
                    user32.SetWindowTextW(ctypes.c_void_p(handle), str(text))
                if node.role == ROLE_CHECKBOX:
                    user32.SendMessageW(
                        ctypes.c_void_p(handle), 0x00F1,
                        1 if node.checked else 0, 0)
        finally:
            self.window._proxy_updating = False
        return tree

    def poll_focus(self):
        import ctypes
        user32 = ctypes.windll.user32
        handle = user32.GetFocus()
        widget = getattr(self.window, "_a11y_by_handle", {}).get(int(handle))
        if widget is not None and widget is not getattr(
                self.window, "focus_widget", None):
            self.window.set_focus(widget)
            handle = self.window._a11y_windows.get(id(widget))
            if handle and int(handle) in getattr(self.window, "_uia_native", set()):
                try:
                    from .uia_native import notify_focus
                    notify_focus(handle)
                except Exception:
                    pass
            return widget
        return None

    def activate(self, widget):
        node = self.tree().find(widget)
        return bool(node and node.activate())

    def set_value(self, widget, text):
        node = self.tree().find(widget)
        return bool(node and node.set_value(text))

    def node(self, widget):
        return self.tree().find(widget)
