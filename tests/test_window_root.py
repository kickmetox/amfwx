"""Window root/layout consistency tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Label, Window


class RootTests(unittest.TestCase):
    def test_layout_add_enters_root(self):
        window = Window("Root", 300, 200)
        try:
            label = Label("Hallo")
            window.layout.add(label)
            window._layout_root()
            self.assertIn(label, window.root.children)
            self.assertIs(window.accessibility_tree().find(label).widget, label)
        finally:
            window.close()
            window.process_events(40)

    def test_no_duplicates(self):
        window = Window("Root", 300, 200)
        try:
            window.layout.add(Label("A"))
            window.layout.add(Label("B"))
            window._layout_root()
            window._layout_root()
            self.assertEqual(len(window.root.children), 2)
        finally:
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
