"""Scanner enumeration tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import list_twain_sources, list_wia_devices


class ScannerTests(unittest.TestCase):
    def test_twain(self):
        sources = list_twain_sources()
        self.assertIsInstance(sources, list)
        for source in sources:
            self.assertTrue(source.product_name)

    def test_wia(self):
        devices = list_wia_devices()
        self.assertIsInstance(devices, list)
        for device in devices:
            self.assertTrue(device.device_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
