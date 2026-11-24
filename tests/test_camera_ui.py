"""Camera window tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, CameraWindow


class CameraUiTests(unittest.TestCase):
    def test_window(self):
        window = CameraWindow()
        try:
            self.assertEqual(window.index.text(), "0")
            self.assertEqual(window.width.text(), "1280")
            self.assertEqual(window.preview_button.text, "Vorschau")
            self.assertEqual(window.seconds.text(), "5")
        finally:
            window.close()

    def test_cli(self):
        self.assertTrue(AppConfig.parse(["--camera-ui"]).camera_ui)


if __name__ == "__main__":
    unittest.main(verbosity=2)
