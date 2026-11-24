"""Scanner window tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, ScannerWindow


class ScannerUiTests(unittest.TestCase):
    def test_window(self):
        window = ScannerWindow()
        try:
            self.assertEqual(window.backend.current_text(), "WIA")
            self.assertEqual(window.dpi.text(), "300")
        finally:
            window.close()

    def test_cli(self):
        self.assertTrue(AppConfig.parse(["--scanner-ui"]).scanner_ui)


if __name__ == "__main__":
    unittest.main(verbosity=2)
