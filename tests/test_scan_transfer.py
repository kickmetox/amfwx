"""Scan transfer tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, transfer_files


class ScanTransferTests(unittest.TestCase):
    def test_transfer_unique(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source"
            target = Path(folder) / "target"
            source.mkdir()
            (source / "page.jpg").write_bytes(b"one")
            first = transfer_files([source / "page.jpg"], target)
            second = transfer_files([source / "page.jpg"], target)
            self.assertNotEqual(first[0], second[0])
            self.assertTrue(Path(first[0]).is_file())
            self.assertTrue(Path(second[0]).is_file())

    def test_cli_parse(self):
        config = AppConfig.parse([
            "--scan-host", "192.168.178.93",
            "--scan-source", "Feeder",
            "--scan-pages", "3",
            "--scan-port", "9096",
        ])
        self.assertEqual(config.scan_host, "192.168.178.93")
        self.assertEqual(config.scan_source, "Feeder")
        self.assertEqual(config.scan_pages, 3)
        self.assertEqual(config.scan_port, 9096)


if __name__ == "__main__":
    unittest.main(verbosity=2)
