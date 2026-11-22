"""Accessibility audit tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (Button, Label, LineEdit, ListBox, RadioButton, Slider,
                   SpinBox, Window)
from amfwx.accessibility import ROLE_CHECKBOX, ROLE_EDIT, ROLE_LIST
from tools.a11y_audit import audit


class A11yTests(unittest.TestCase):
    def test_audit_demo(self):
        window = Window("A11y", 400, 300)
        try:
            window.add(Label("Name"))
            field = LineEdit("")
            field.accessible_name = "Name"
            window.add(field)
            window.add(Button("OK"))
            window.add(RadioButton("A"))
            slider = Slider(0, 100, 5)
            slider.accessible_name = "Wert"
            window.add(slider)
            window.add(SpinBox(5))
            window.add(ListBox(["A"]))
            result = audit(window)
            self.assertTrue(result["ok"], result["errors"])
        finally:
            window.close()
            window.process_events(40)

    def test_roles(self):
        window = Window("Roles", 300, 200)
        try:
            radio = RadioButton("A")
            spin = SpinBox(3)
            listing = ListBox(["A"])
            for widget in (radio, spin, listing):
                window.add(widget)
            tree = window.accessibility_tree()
            self.assertEqual(tree.find(radio).role, ROLE_CHECKBOX)
            self.assertEqual(tree.find(spin).role, ROLE_EDIT)
            self.assertEqual(tree.find(spin).value, "3")
            self.assertEqual(tree.find(listing).role, ROLE_LIST)
        finally:
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
