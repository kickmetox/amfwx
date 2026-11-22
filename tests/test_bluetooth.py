"""Bluetooth enumeration tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import list_bluetooth_devices, list_radios


class BluetoothTests(unittest.TestCase):
    def test_radios(self):
        radios = list_radios()
        self.assertIsInstance(radios, list)
        for radio in radios:
            self.assertTrue(radio.name)
            self.assertIn(":", radio.address)

    def test_devices(self):
        devices = list_bluetooth_devices(issue_inquiry=False)
        self.assertIsInstance(devices, list)
        for device in devices:
            self.assertIn("address", device)
            self.assertIn("connected", device)


if __name__ == "__main__":
    unittest.main(verbosity=2)
