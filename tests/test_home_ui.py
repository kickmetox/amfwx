"""Home discovery panel tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import HomeRegistry
from amfwx.home_ui import HomeDevicesPanel


class Device:
    kind = "shelly"
    name = "Shelly"
    host = "127.0.0.1"
    port = 80


class PanelTests(unittest.TestCase):
    def test_set_devices(self):
        panel = HomeDevicesPanel(HomeRegistry())
        panel.set_devices([Device()])
        self.assertEqual(len(panel.rows.children), 1)
        self.assertIn("1", panel.status.text)

    def test_add(self):
        registry = HomeRegistry()
        added = []
        panel = HomeDevicesPanel(registry, on_added=added.append)
        entry = panel.add_device(Device())
        self.assertIn(entry["id"], registry.devices)
        self.assertEqual(added[0]["kind"], "shelly")

    def test_remove(self):
        registry = HomeRegistry()
        panel = HomeDevicesPanel(registry)
        entry = panel.add_device(Device())
        self.assertIn(entry["id"], registry.devices)
        panel.remove_device(entry["id"])
        self.assertNotIn(entry["id"], registry.devices)


if __name__ == "__main__":
    unittest.main(verbosity=2)
