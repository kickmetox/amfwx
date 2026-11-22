"""Settings persistence tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Settings, Window


class SettingsTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "settings.json")
            settings = Settings(path)
            settings.set("theme", "dark")
            settings.add_recent("a.txt")
            settings.add_recent("b.txt")
            restored = Settings(path)
            self.assertEqual(restored.get("theme"), "dark")
            self.assertEqual(restored.recent()[:2], ["b.txt", "a.txt"])

    def test_window_geometry(self):
        with tempfile.TemporaryDirectory() as folder:
            settings = Settings(os.path.join(folder, "settings.json"))
            window = Window("Geometry", 420, 320)
            try:
                window.save_geometry(settings)
                geometry = settings.get("window_geometry")
                self.assertIn("width", geometry)
                self.assertTrue(window.restore_geometry(geometry))
            finally:
                window.close()
                window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
