"""AMFWX internal drag-and-drop."""

from __future__ import annotations


class DragEvent:
    def __init__(self, data=None, source=None, x=0, y=0, text=""):
        self.data = data
        self.source = source
        self.x = x
        self.y = y
        self.text = text
        self.accepted = False

    def accept(self):
        self.accepted = True


class DragManager:
    def __init__(self, window):
        self.window = window
        self.active = False
        self.data = None
        self.source = None
        self.position = (0, 0)

    def start(self, data=None, source=None, x=None, y=None):
        self.active = True
        self.data = data
        self.source = source
        self.position = (x or 0, y or 0)
        return self

    def finish(self, x, y):
        if not self.active:
            return False
        self.active = False
        target = self.window._widget_at(x, y)
        if target is None:
            return False
        event = DragEvent(self.data, self.source, x, y)
        node = target
        while node is not None:
            if hasattr(node, "drop_event"):
                node.drop_event(event)
                if event.accepted:
                    return True
            node = getattr(node, "parent", None)
        return False
