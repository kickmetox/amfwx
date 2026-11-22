"""AMFWX window smoke test."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import BoxLayout, Button, Label, Window


class WindowTests(unittest.TestCase):
    def test_render_window(self):
        window = Window("AMFWX Test", 480, 320)
        layout = BoxLayout(spacing=8, padding=16)
        layout.add(Label("AMFWX"), 0)
        layout.add(Button("OK"), 0)
        window.layout = layout
        window.root.children.clear()
        for widget, _stretch in layout.items:
            window.root.add(widget)
        window._layout_root()
        window.invalidate()
        window.process_events(40)
        try:
            with tempfile.TemporaryDirectory() as folder:
                path = os.path.join(folder, "window.bmp")
                self.assertEqual(window.render_to_bmp(path), path)
                self.assertGreater(os.path.getsize(path), 54)
        finally:
            window.close()
            window.process_events(80)


if __name__ == "__main__":
    unittest.main(verbosity=2)
