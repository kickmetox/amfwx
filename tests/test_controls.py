"""AMFWX controls, focus, layouts and dialogs."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (
    DARK, LIGHT, BoxLayout, Button, CheckBox, Dialog, FormLayout, GridLayout,
    Label, LineEdit, Slider, Window,
)
from amfwx.widgets import VK_BACK, VK_LEFT, VK_RIGHT


class ControlTests(unittest.TestCase):
    def test_focus_and_lineedit(self):
        window = Window("controls", 500, 320)
        edit = LineEdit("ab")
        window.layout = BoxLayout()
        window.root.children.clear()
        window.root.add(edit)
        window.layout.add(edit)
        window._layout_root()
        window.set_focus(edit)
        edit.char_input("c")
        self.assertEqual(edit.text(), "abc")
        window._key_down(VK_LEFT)
        window._key_down(VK_BACK)
        self.assertEqual(edit.text(), "ac")
        window._key_down(VK_RIGHT)
        edit.char_input("d")
        self.assertEqual(edit.text(), "acd")
        window.close()
        window.process_events(40)

    def test_checkbox_and_slider(self):
        changes = []
        check = CheckBox("aktiv", False, on_change=changes.append)
        check.toggle()
        self.assertTrue(check.checked)
        self.assertEqual(changes, [True])
        slider = Slider(0, 10, 5)
        slider.set_value(20)
        self.assertEqual(slider.value(), 10)
        slider.set_value(-5)
        self.assertEqual(slider.value(), 0)

    def test_grid_and_form(self):
        grid = GridLayout(columns=2)
        first, second = Label("A"), Label("B")
        grid.add(first, 0, 0)
        grid.add(second, 0, 1)
        root = Label("root")
        grid.arrange(root, type("R", (), {"x": 0, "y": 0, "w": 300,
                                           "h": 100})())
        self.assertLess(first.rect.x, second.rect.x)
        form = FormLayout()
        label, field = Label("Name"), LineEdit()
        form.add(label, field)
        form.arrange(root, type("R", (), {"x": 0, "y": 0, "w": 300,
                                           "h": 100})())
        self.assertLess(label.rect.x, field.rect.x)

    def test_dialog_and_theme(self):
        parent = Window("parent", 400, 300)
        dialog = Dialog(parent, "Info", 300, 160)
        self.assertIs(dialog.parent_window, parent)
        dialog.close()
        parent.set_theme(LIGHT)
        self.assertIs(parent.theme, LIGHT)
        parent.close()
        parent.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
