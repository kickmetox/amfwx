"""Scan window tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, ScanWindow


class ScanUiTests(unittest.TestCase):
    def test_window(self):
        window = ScanWindow()
        try:
            self.assertEqual(window.port.text(), "9096")
            self.assertFalse(window.ocr.checked)
            self.assertEqual(window.language.text(), "de-DE")
            self.assertFalse(window.pdf.checked)
        finally:
            window.close()

    def test_cli(self):
        self.assertTrue(AppConfig.parse(["--scan-ui"]).scan_ui)


if __name__ == "__main__":
    unittest.main(verbosity=2)
