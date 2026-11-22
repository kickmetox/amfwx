"""Scanner enumeration tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import WiaError, WiaScanner, dsm_available, list_twain_sources, list_wia_devices


class ScannerTests(unittest.TestCase):
    def test_dsm(self):
        self.assertTrue(dsm_available())
    def test_twain(self):
        sources = list_twain_sources()
        self.assertIsInstance(sources, list)
        for source in sources:
            self.assertTrue(source.product_name)

    def test_wia_missing_device(self):
        with self.assertRaises(WiaError):
            WiaScanner(device_id="missing").acquire("x.png")

    def test_wia(self):
        devices = list_wia_devices()
        self.assertIsInstance(devices, list)
        for device in devices:
            self.assertTrue(device.device_id)

    def test_wia_settings(self):
        values = WiaScanner._settings(300, 1, True)
        self.assertIn(("6146", 300), values)
        self.assertIn(("6147", 300), values)
        self.assertIn(("6148", 1), values)
        self.assertIn(("3088", 1), values)

    def test_page_path(self):
        self.assertTrue(WiaScanner._page_path("scan.png", 2).endswith(
            "scan_002.png"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
