"""Home registry tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import HomeRegistry


class Device:
    kind = "shelly"
    name = "Shelly Test"
    host = "127.0.0.1"
    port = 80


class RegistryTests(unittest.TestCase):
    def test_add_and_adapter(self):
        registry = HomeRegistry()
        entry = registry.add(Device())
        self.assertIn(entry["id"], registry.devices)
        self.assertEqual(type(registry.adapter(entry["id"])).__name__,
                         "ShellyDevice")

    def test_save_load(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "devices.json")
            registry = HomeRegistry(path)
            registry.add(Device())
            registry.save()
            loaded = HomeRegistry(path)
            self.assertEqual(len(loaded.devices), 1)
            self.assertEqual(next(iter(loaded.devices.values()))["kind"],
                             "shelly")

    def test_generic(self):
        class Generic:
            kind = "homepilot"
            name = "HomePilot"
            host = "127.0.0.1"
            port = 80

        registry = HomeRegistry()
        entry = registry.add(Generic(), {"status_path": "/api/status",
                                         "command_path": "/api/command"})
        adapter = registry.adapter(entry["id"])
        self.assertEqual(adapter.status_path, "/api/status")

    def test_update(self):
        registry = HomeRegistry()
        entry = registry.add(Device())
        updated = registry.update(entry["id"], password="secret")
        self.assertEqual(updated["config"]["password"], "secret")


if __name__ == "__main__":
    unittest.main(verbosity=2)
