"""Resource and crash logging tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import CrashLogger, ResourcePack


class ResourceTests(unittest.TestCase):
    def test_pack(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "pack.zip")
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("theme.json", '{"name":"dark"}')
                archive.writestr("i18n/de.json", '{"ok":"OK"}')
            with ResourcePack(path) as pack:
                self.assertEqual(pack.json("theme.json")["name"], "dark")
                self.assertEqual(pack.text("i18n/de.json"), '{"ok":"OK"}')
                self.assertTrue(pack.exists("theme.json"))
                self.assertFalse(pack.exists("missing"))


class CrashTests(unittest.TestCase):
    def test_log(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "crash.log")
            logger = CrashLogger(path)
            try:
                raise ValueError("boom")
            except ValueError as error:
                logger.log(error, "test")
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            self.assertIn("ValueError: boom", text)
            self.assertIn("context: test", text)

    def test_install(self):
        with tempfile.TemporaryDirectory() as folder:
            logger = CrashLogger(os.path.join(folder, "crash.log"))
            previous = sys.excepthook
            logger.install()
            self.assertIsNot(sys.excepthook, previous)
            logger.uninstall()
            self.assertIs(sys.excepthook, previous)


if __name__ == "__main__":
    unittest.main(verbosity=2)
