"""Self-developed AMFWX engines: TTF, PNG, software 3D."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Canvas, Color
from amfwx.font import TrueTypeFont
from amfwx.render3d import (
    SoftwareRenderer, cube, look_at, multiply, perspective, rotate_y,
    translate,
)


class EngineTests(unittest.TestCase):
    def test_png_roundtrip(self):
        canvas = Canvas(24, 16, Color(0, 0, 0))
        canvas.fill_rect(__import__("amfwx").Rect(2, 2, 5, 4),
                         Color(255, 0, 0))
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "x.png")
            canvas.save_png(path)
            loaded = Canvas.from_png(path)
            self.assertEqual(loaded.pixel(3, 3), Color(255, 0, 0, 255))
            self.assertEqual(loaded.pixel(0, 0), Color(0, 0, 0, 255))

    def test_truetype_subset(self):
        path = r"C:\Windows\Fonts\segoeui.ttf"
        if not os.path.exists(path):
            self.skipTest("Segoe UI nicht vorhanden")
        font = TrueTypeFont(path, 20)
        self.assertGreater(len(font.cmap), 100)
        self.assertGreater(font.measure("Hello"), 0)
        canvas = Canvas(160, 40, Color(0, 0, 0))
        font.draw(canvas, "Hello", 2, 2, Color(255, 255, 255))
        self.assertGreater(canvas.pixel(5, 10).r, 0)

    def test_software_3d(self):
        canvas = Canvas(120, 100, Color(10, 12, 18))
        model = multiply(translate(0, 0, -3), rotate_y(0.4))
        view = look_at((0, 0, 2), (0, 0, 0))
        projection = perspective(60, 1.2, 0.1, 100)
        SoftwareRenderer(120, 100).render(
            canvas, cube(1.5), multiply(projection, multiply(view, model)))
        colored = sum(1 for x in range(0, 120, 8) for y in range(0, 100, 8)
                      if canvas.pixel(x, y) != Color(10, 12, 18))
        self.assertGreater(colored, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
