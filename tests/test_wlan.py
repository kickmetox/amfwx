"""WLAN scan tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import list_wlan_interfaces, scan_wlan


class WlanTests(unittest.TestCase):
    def test_interfaces(self):
        interfaces = list_wlan_interfaces()
        self.assertIsInstance(interfaces, list)
        for interface in interfaces:
            self.assertTrue(interface.description)

    def test_scan(self):
        networks = scan_wlan()
        self.assertIsInstance(networks, list)
        for network in networks:
            self.assertIsInstance(network.ssid, str)
            self.assertGreaterEqual(network.quality, 0)
            self.assertLessEqual(network.quality, 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
