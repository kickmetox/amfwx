"""AMFWX editor integration test."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.editor import EditorWindow


class EditorTests(unittest.TestCase):
    def test_edit_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "note.txt"
            path.write_text("alt", encoding="utf-8")
            window = EditorWindow(path)
            window.process_events(40)
            try:
                self.assertEqual(window.editor.text(), "alt")
                self.assertTrue(any(item.label == "note.txt"
                                    for item in window.recent_menu.actions))
                window.editor.set_text("neu")
                self.assertTrue(window.dirty)
                self.assertTrue(window.save_file())
                self.assertFalse(window.dirty)
                self.assertEqual(path.read_text(encoding="utf-8"), "neu")
                window.new_file()
                self.assertEqual(window.editor.text(), "")
                self.assertEqual(window.path, "")
            finally:
                window.close()
                window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
