"""AMFWX popup, menu, table and tree controls."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (
    BoxLayout, Button, ComboBox, Label, MenuBar, Rect, ScrollArea,
    ScrollBar, TableView, TreeItem, TreeView, Window,
)


class AdvancedControlTests(unittest.TestCase):
    def test_combobox_popup(self):
        window = Window("combo", 420, 300)
        combo = ComboBox(["A", "B", "C"], 0)
        window.layout = BoxLayout()
        window.root.children.clear()
        window.root.add(combo)
        window.layout.add(combo)
        window._layout_root()
        combo.open_popup()
        self.assertIsNotNone(window.overlay)
        popup = window.overlay
        window._mouse_up(popup.rect.x + 8, popup.rect.y + 32)
        self.assertEqual(combo.current_index, 1)
        window.close()
        window.process_events(40)

    def test_scrollbar_and_area(self):
        changed = []
        bar = ScrollBar(maximum=200, page=80, on_change=changed.append)
        bar.arrange(Rect(0, 0, 14, 200))
        bar.set_value(50)
        self.assertEqual(bar.value, 50)
        self.assertEqual(changed[-1], 50)
        area = ScrollArea(content=Label("content"), content_height=500)
        area.arrange(Rect(0, 0, 300, 200))
        area.wheel(-120)
        self.assertGreater(area.scroll_y, 0)

    def test_menu_popup(self):
        clicked = []
        window = Window("menu", 500, 300)
        menubar = MenuBar()
        file_menu = menubar.add_menu("Datei")
        file_menu.add("Öffnen", lambda: clicked.append("open"), "Ctrl+O")
        window.root.children.clear()
        window.root.add(menubar)
        menubar.arrange(Rect(0, 0, 500, 30))
        menubar.paint(window.canvas)
        menubar.mouse_up(20, 15)
        self.assertIsNotNone(window.overlay)
        popup = window.overlay
        window._mouse_up(popup.rect.x + 8, popup.rect.y + 8)
        self.assertEqual(clicked, ["open"])
        window.close()
        window.process_events(40)

    def test_table_and_tree(self):
        rows = [["A", "1"], ["B", "2"]]
        table = TableView(["Name", "Wert"], rows)
        table.arrange(Rect(0, 0, 300, 200))
        table.mouse_up(10, table.rect.y + table.header_height + 5)
        self.assertEqual(table.selected, 0)
        tree = TreeView([TreeItem("Root", [TreeItem("Child")])])
        tree.arrange(Rect(0, 0, 300, 200))
        tree.mouse_up(50, tree.rect.y + 10)
        self.assertIsNotNone(tree.selected)


    def test_internal_drag_drop(self):
        class Drop(Label):
            def __init__(self):
                super().__init__("drop")
                self.data = None

            def drop_event(self, event):
                self.data = event.data
                event.accept()

        window = Window("dnd", 400, 300)
        target = Drop()
        target.arrange(Rect(20, 20, 200, 100))
        window.root.children.clear()
        window.root.add(target)
        window.start_drag({"id": 3})
        window._mouse_up(30, 30)
        self.assertEqual(target.data, {"id": 3})
        window.close()
        window.process_events(40)

    def test_table_edit_and_tree_toggle(self):
        table = TableView(["A"], [["x"]])
        table.arrange(Rect(0, 0, 300, 200))
        table.selected = 0
        editor = table.begin_edit()
        self.assertIsNotNone(editor)
        editor.set_text("neu")
        table.commit_edit()
        self.assertEqual(table.rows[0][0], "neu")
        item = TreeItem("Root", [TreeItem("Child")])
        tree = TreeView([item])
        tree.arrange(Rect(0, 0, 300, 200))
        tree.mouse_up(5, 10)
        self.assertFalse(item.expanded)


if __name__ == "__main__":
    unittest.main(verbosity=2)
