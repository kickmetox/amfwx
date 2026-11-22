"""PDF export tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Canvas, Color, Window


class PdfTests(unittest.TestCase):
    def test_canvas_pdf(self):
        canvas = Canvas(40, 20, Color(255, 0, 0))
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "canvas.pdf")
            canvas.save_pdf(path)
            with open(path, "rb") as handle:
                data = handle.read()
            self.assertTrue(data.startswith(b"%PDF-1.4"))
            self.assertIn(b"/MediaBox [0 0 40 20]", data)
            self.assertIn(b"/Count 1", data)

    def test_window_pdf(self):
        window = Window("PDF", 120, 80)
        try:
            with tempfile.TemporaryDirectory() as folder:
                path = os.path.join(folder, "window.pdf")
                window.render_to_pdf(path)
                self.assertGreater(os.path.getsize(path), 100)
        finally:
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
