"""RadioButton, SpinBox and ListBox tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Canvas, ListBox, RadioButton, Rect, SpinBox


class MoreWidgetsTests(unittest.TestCase):
    def test_radio_group(self):
        group = []
        first = RadioButton("A", group=group, checked=True)
        second = RadioButton("B", group=group)
        second.select()
        self.assertFalse(first.checked)
        self.assertTrue(second.checked)
        Canvas(120, 40).fill_rect(Rect(0, 0, 1, 1), first.theme().text)

    def test_spinbox(self):
        spin = SpinBox(5, 0, 10, 2)
        spin.increment(1)
        self.assertEqual(spin.value(), 7)
        spin.increment(-2)
        self.assertEqual(spin.value(), 3)
        spin.set_value(99)
        self.assertEqual(spin.value(), 10)

    def test_listbox(self):
        selected = []
        box = ListBox(["A", "B", "C"], on_select=selected.append)
        box.arrange(Rect(0, 0, 200, 120))
        box.mouse_up(10, 4 + 26 + 5)
        self.assertEqual(box.selected_item(), "B")
        self.assertEqual(selected, ["B"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
