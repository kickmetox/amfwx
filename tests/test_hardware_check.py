"""Hardware diagnostic tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.hardware_check import build_report


class HardwareCheckTests(unittest.TestCase):
    def test_report(self):
        report = build_report()
        for key in ("serial", "hid", "usb", "bluetooth", "wlan", "displays"):
            self.assertIn(key, report["devices"])
            self.assertIsInstance(report["devices"][key], int)
        self.assertIn("pcan", report["backends"])
        self.assertIn("firewire", report["unsupported"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
