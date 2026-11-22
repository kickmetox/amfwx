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
            self.assertEqual(len(window.palette.children), 11)
            window.document.add("button", "OK", 20, 20, 100, 32)
            self.assertIn("Button", window.generate_code())
        finally:
            window.close()
            window.process_events(40)

    def test_undo_redo(self):
        document = DesignerDocument()
        document.add("label", "A", 10, 10, 80, 24)
        document.move(0, 40, 50)
        self.assertEqual((document.items[0].x, document.items[0].y), (40, 50))
        self.assertTrue(document.undo())
        self.assertEqual((document.items[0].x, document.items[0].y), (10, 10))
        self.assertTrue(document.redo())
        self.assertEqual((document.items[0].x, document.items[0].y), (40, 50))

    def test_resize_handle(self):
        document = DesignerDocument()
        item = document.add("label", "A", 20, 20, 80, 24)
        view = DesignerCanvas(document)
        view.arrange(Rect(0, 0, 400, 300))
        view.mouse_down(20 + 80 - 2, 20 + 24 - 2)
        view.mouse_move(140, 90)
        view.mouse_up(140, 90)
        self.assertGreater(item.width, 80)
        self.assertGreater(item.height, 24)


if __name__ == "__main__":
    unittest.main(verbosity=2)
