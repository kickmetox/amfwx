"""AMFWX rasterizer, text and layout tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import BoxLayout, Canvas, Color, Label, Rect, measure_text
from amfwx.text import draw_text


class CanvasTests(unittest.TestCase):
    def test_fill_and_pixel(self):
        canvas = Canvas(20, 10, Color(0, 0, 0))
        canvas.fill_rect(Rect(2, 2, 5, 4), Color(255, 0, 0))
        self.assertEqual(canvas.pixel(3, 3), Color(255, 0, 0, 255))
        self.assertEqual(canvas.pixel(0, 0), Color(0, 0, 0, 255))

    def test_polygon_and_alpha(self):
        canvas = Canvas(20, 20)
        canvas.fill_polygon([(2, 2), (18, 2), (10, 18)],
                            Color(0, 255, 0, 128))
        self.assertGreater(canvas.pixel(10, 5).g, 0)
        self.assertLess(canvas.pixel(10, 5).g, 255)

    def test_text_and_layout(self):
        canvas = Canvas(200, 40, Color(0, 0, 0))
        draw_text(canvas, "AMFWX", 4, 4, Color(255, 255, 255), 2)
        self.assertGreater(measure_text("AMFWX", 2), 0)
        self.assertEqual(canvas.pixel(6, 4).r, 255)
        label = Label("Hi")
        self.assertGreater(label.size_hint()[0], 0)

    def test_bmp_export(self):
        import tempfile
        canvas = Canvas(20, 10)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "x.bmp")
            canvas.save_bmp(path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 54)


if __name__ == "__main__":
    unittest.main(verbosity=2)
