"""ColorPicker and FilePicker tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Canvas, Color, ColorPicker, FilePicker, Rect


class PickerTests(unittest.TestCase):
    def test_color_picker(self):
        changed = []
        picker = ColorPicker(Color(1, 2, 3), on_change=changed.append)
        picker.arrange(Rect(0, 0, 120, 30))
        picker.paint(Canvas(120, 30))
        picker.set_color(Color(10, 20, 30))
        self.assertEqual(picker.color.r, 10)
        self.assertEqual(len(changed), 1)

    def test_file_picker(self):
        changed = []
        picker = FilePicker("", on_change=changed.append)
        picker.arrange(Rect(0, 0, 280, 30))
        picker.paint(Canvas(280, 30))
        picker.set_path("C:\\temp\\a.txt")
        self.assertEqual(picker.path, "C:\\temp\\a.txt")
        self.assertEqual(changed, ["C:\\temp\\a.txt"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
