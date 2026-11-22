"""Deterministic widget fuzz test."""

from __future__ import annotations

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (
    Canvas, Color, Rect, TabView, TableView, TextEdit, TreeItem, TreeView,
    Window,
)
from amfwx.advanced import Property, PropertyGrid

KEYS = [8, 9, 13, 27, 37, 38, 39, 40, 46, 65, 67, 86, 88, 89, 90]
CHARS = list("abc XYZ 0123\n\täöü")


class FuzzTests(unittest.TestCase):
    def test_random_widget_input(self):
        random.seed(12345)
        window = Window("Fuzz", 640, 480)
        editor = TextEdit("start")
        table = TableView(["A", "B"], [["1", "2"], ["3", "4"]])
        tree = TreeView([TreeItem("root", [TreeItem("child")])])
        tabs = TabView()
        tabs.add_tab("A", editor)
        tabs.add_tab("B", table)
        window.root.children.clear()
        window.root.add(tabs)
        window.root.add(tree)
        window.root.add(PropertyGrid([Property("x", "X", "int", 1)]))
        window._layout_root()
        canvas = Canvas(640, 480)
        widgets = [editor, table, tree, tabs]
        for index in range(400):
            widget = random.choice(widgets)
            action = random.randrange(6)
            x = random.randrange(0, 640)
            y = random.randrange(0, 480)
            try:
                if action == 0:
                    widget.key_down(random.choice(KEYS),
                                    random.choice([0, 1, 2, 3]))
                elif action == 1:
                    widget.char_input(random.choice(CHARS))
                elif action == 2:
                    widget.mouse_down(x, y)
                elif action == 3:
                    widget.mouse_move(x, y)
                elif action == 4:
                    widget.mouse_up(x, y)
                else:
                    widget.paint(canvas)
                window.process_events(0)
            except Exception as error:
                self.fail(f"Fuzz-Exception bei Iteration {index}: {error!r}")
        window.close()
        window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
