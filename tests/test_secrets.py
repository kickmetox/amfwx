"""DPAPI and encrypted registry tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import HomeRegistry
from amfwx.secrets import protect_text, unprotect_text


class SecretTests(unittest.TestCase):
    def test_roundtrip(self):
        encrypted = protect_text("secret")
        self.assertTrue(encrypted.startswith("dpapi:"))
        self.assertNotIn("secret", encrypted)
        self.assertEqual(unprotect_text(encrypted), "secret")

    def test_registry_encrypts(self):
        class Device:
            kind = "fibaro"
            name = "Fibaro"
            host = "127.0.0.1"
            port = 80

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "devices.json")
            registry = HomeRegistry(path)
            entry = registry.add(Device(), {"password": "secret"})
            registry.save()
            with open(path, encoding="utf-8") as handle:
                raw = handle.read()
            self.assertNotIn("secret", raw)
            loaded = HomeRegistry(path)
            self.assertEqual(loaded.devices[entry["id"]]["config"]["password"],
                             "secret")


if __name__ == "__main__":
    unittest.main(verbosity=2)
