"""Device inventory tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import DeviceManager, list_devices


class DeviceTests(unittest.TestCase):
    def test_list(self):
        devices = list_devices()
        for key in ("serial", "hid", "usb", "bluetooth", "wlan", "displays",
                    "network"):
            self.assertIn(key, devices)
            self.assertIsInstance(devices[key], list)

    def test_manager(self):
        manager = DeviceManager().refresh()
        summary = manager.summary()
        self.assertIn("serial", summary)
        self.assertIsInstance(manager.get("displays"), list)

    def test_network(self):
        manager = DeviceManager().refresh()
        self.assertIn("network", manager.snapshot)
        self.assertIsInstance(manager.snapshot["network"], list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
