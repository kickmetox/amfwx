"""Security helper tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import ResourcePack, SecurityError, safe_resource_name
from amfwx.security import safe_join, verify_native_dlls


class SecurityTests(unittest.TestCase):
    def test_native_manifest(self):
        result = verify_native_dlls(strict=True)
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["mismatched"], [])

    def test_resource_names(self):
        self.assertEqual(safe_resource_name("theme.json"), "theme.json")
        for name in ("../secret", "a/../../b", "/etc/passwd",
                     "C:/Windows/win.ini"):
            with self.assertRaises(SecurityError):
                safe_resource_name(name)

    def test_zip_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "pack.zip")
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../escape.txt", "x")
            with ResourcePack(path) as pack:
                with self.assertRaises(SecurityError):
                    pack.read("../escape.txt")
            with self.assertRaises(SecurityError):
                safe_join(folder, "../escape.txt")


if __name__ == "__main__":
    unittest.main(verbosity=2)
