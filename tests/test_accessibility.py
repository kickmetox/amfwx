"""Accessibility provider model tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Button, Label, LineEdit, Window


class AccessibilityTreeTests(unittest.TestCase):
    def test_tree_and_label(self):
        window = Window("Formular", 400, 300)
        edit = LineEdit("Text")
        window.root.add(Label("Name", label_for=edit))
        window.root.add(edit)
        window.root.add(Button("OK"))
        window._layout_root()
        tree = window.accessibility_tree()
        nodes = list(tree.walk())
        self.assertEqual(nodes[0].role, "window")
        edit_node = tree.find(edit)
        self.assertEqual(edit_node.role, "edit")
        self.assertEqual(edit_node.name, "Name")
        self.assertEqual(edit_node.value, "Text")
        button_node = tree.find(window.root.children[2])
        self.assertEqual(button_node.name, "OK")
        window.close()
        window.process_events(40)

    def test_actions(self):
        clicked = []
        window = Window("Aktionen", 400, 300)
        button = Button("OK", on_click=lambda: clicked.append(1))
        edit = LineEdit("alt")
        window.root.add(button)
        window.root.add(edit)
        window._layout_root()
        tree = window.accessibility_tree()
        self.assertTrue(tree.find(button).activate())
        self.assertEqual(clicked, [1])
        self.assertTrue(tree.find(edit).set_value("neu"))
        self.assertEqual(edit.text(), "neu")
        window.close()
        window.process_events(40)

    def test_bridge_coupling(self):
        import ctypes
        window = Window("Brücke", 400, 300)
        button = Button("Alt")
        edit = LineEdit("Wert")
        window.root.add(button)
        window.root.add(edit)
        window._layout_root()
        window.sync_accessibility()
        bridge = window.accessibility_bridge()
        button_handle = window._a11y_windows[id(button)]
        buffer = ctypes.create_unicode_buffer(64)
        ctypes.windll.user32.GetWindowTextW(button_handle, buffer, 64)
        self.assertEqual(buffer.value, "Alt")
        button.text = "Neu"
        window.invalidate()
        ctypes.windll.user32.GetWindowTextW(button_handle, buffer, 64)
        self.assertEqual(buffer.value, "Neu")
        self.assertTrue(bridge.activate(button))
        ctypes.windll.user32.SetFocus(ctypes.c_void_p(
            window._a11y_windows[id(edit)]))
        window.process_events(120)
        self.assertIs(window.focus_widget, edit)
        window.close()
        window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
