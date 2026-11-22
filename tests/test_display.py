"""Display/monitor tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (Window, exit_fullscreen, fullscreen, list_monitors,
                   monitor_work_area, primary_monitor)


class DisplayTests(unittest.TestCase):
    def test_monitors(self):
        monitors = list_monitors()
        self.assertGreaterEqual(len(monitors), 1)
        primary = primary_monitor()
        self.assertIsNotNone(primary)
        self.assertGreater(primary.width, 0)
        self.assertGreater(primary.height, 0)

    def test_fullscreen_roundtrip(self):
        window = Window("Display", 320, 200)
        try:
            self.assertIsNotNone(fullscreen(window))
            self.assertIsNotNone(monitor_work_area(window))
            exit_fullscreen(window)
        finally:
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
