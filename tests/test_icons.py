"""Runtime icon tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (TrayIcon, Window, default_icon_path, load_icon,
                   set_window_icon)


class IconTests(unittest.TestCase):
    def test_default_icon(self):
        path = default_icon_path()
        self.assertIsNotNone(path)
        self.assertTrue(path.is_file())
        self.assertIsNotNone(load_icon())

    def test_window_and_tray(self):
        window = Window("Icon", 240, 140)
        tray = TrayIcon(window)
        try:
            self.assertTrue(set_window_icon(window))
            self.assertTrue(tray.add())
        finally:
            tray.remove()
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
