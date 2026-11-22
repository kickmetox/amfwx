"""UIA-shaped accessibility tree for AMFWX (no COM provider yet)."""

from __future__ import annotations

from dataclasses import dataclass, field


_ROLES = {
    "Window": "Window",
    "Label": "Text",
    "Button": "Button",
    "LineEdit": "Edit",
    "CheckBox": "CheckBox",
    "Slider": "Slider",
    "ComboBox": "ComboBox",
    "TableView": "DataGrid",
    "TreeView": "Tree",
    "MenuBar": "MenuBar",
    "ScrollArea": "Pane",
}


@dataclass
class UiaNode:
    role: str
    name: str = ""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    enabled: bool = True
    focusable: bool = False
    focused: bool = False
    children: list = field(default_factory=list)

    def as_dict(self):
        return {
            "role": self.role,
            "name": self.name,
            "bounds": {"x": self.x, "y": self.y,
                       "width": self.width, "height": self.height},
            "enabled": self.enabled,
            "focusable": self.focusable,
            "focused": self.focused,
            "children": [child.as_dict() for child in self.children],
        }


def node_from_widget(widget):
    role = _ROLES.get(type(widget).__name__, "Pane")
    rect = getattr(widget, "rect", None)
    node = UiaNode(
        role, getattr(widget, "text", ""), int(rect.x) if rect else 0,
        int(rect.y) if rect else 0, int(rect.w) if rect else 0,
        int(rect.h) if rect else 0, getattr(widget, "enabled", True),
        getattr(widget, "focusable", False), getattr(widget, "focused", False))
    for child in getattr(widget, "children", []):
        node.children.append(node_from_widget(child))
    return node


def tree_from_window(window):
    node = node_from_widget(window.root)
    node.role = "Window"
    node.name = window.title
    node.width = window.width
    node.height = window.height
    return node
