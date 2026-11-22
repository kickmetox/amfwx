"""Designer document/canvas tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (Canvas, DesignerCanvas, DesignerDocument, DesignerWindow,
                   Rect)


class DesignerTests(unittest.TestCase):
    def test_document_roundtrip_and_code(self):
        document = DesignerDocument("Demo")
        document.add("label", "Name", 10, 10, 120, 24)
        document.add("button", "OK", 10, 50, 100, 32)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "form.json")
            document.save(path)
            loaded = DesignerDocument.load(path)
            self.assertEqual(loaded.title, "Demo")
            self.assertEqual(len(loaded.items), 2)
            self.assertIn("Button('OK')", loaded.generate_code())
            self.assertIn("window.run()", loaded.generate_code())

    def test_canvas_select_and_move(self):
        document = DesignerDocument()
        item = document.add("label", "Text", 20, 20, 100, 24)
        canvas = Canvas(400, 300)
        view = DesignerCanvas(document)
        view.arrange(Rect(0, 0, 400, 300))
        view.paint(canvas)
        view.mouse_down(30, 30)
        self.assertEqual(document.selected, 0)
        view.mouse_move(80, 70)
        view.mouse_up(80, 70)
        self.assertEqual((item.x, item.y), (70, 60))

    def test_window(self):
        window = DesignerWindow()
        try:
            self.assertEqual(len(window.palette.children), 8)
            window.document.add("button", "OK", 20, 20, 100, 32)
            self.assertIn("Button", window.generate_code())
        finally:
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
