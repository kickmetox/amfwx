"""USB HID tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import UsbError, list_hid_devices


class UsbTests(unittest.TestCase):
    def test_list(self):
        devices = list_hid_devices()
        self.assertIsInstance(devices, list)
        for device in devices:
            self.assertTrue(device.path)
            self.assertGreater(device.vendor_id, 0)

    def test_invalid_path(self):
        from amfwx import HidDevice
        with self.assertRaises(UsbError):
            HidDevice("\\\\?\\invalid").open()


if __name__ == "__main__":
    unittest.main(verbosity=2)
