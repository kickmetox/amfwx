"""Raw USB/WinUSB tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import UsbRawError, WinUsbDevice, list_usb_devices


class RawUsbTests(unittest.TestCase):
    def test_list(self):
        devices = list_usb_devices()
        self.assertIsInstance(devices, list)
        for device in devices:
            self.assertTrue(device.path)

    def test_invalid(self):
        with self.assertRaises(UsbRawError):
            WinUsbDevice("\\\\?\\invalid").open()


if __name__ == "__main__":
    unittest.main(verbosity=2)
