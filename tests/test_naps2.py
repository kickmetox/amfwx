"""NAPS2 adapter tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Naps2Scanner


class Result:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class Naps2Tests(unittest.TestCase):
    def test_list(self):
        def runner(command, **kwargs):
            if "wia" in command:
                return Result("Canon CanoScan\n")
            return Result("VueScan TWAIN\n")

        scanner = Naps2Scanner(exe="fake.exe", runner=runner)
        sources = scanner.list_sources()
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0].driver, "wia")

    def test_scan(self):
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            Path(command[command.index("-o") + 1]).write_bytes(b"JPG")
            return Result()

        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "scan.jpg")
            scanner = Naps2Scanner(exe="fake.exe", runner=runner)
            self.assertEqual(scanner.scan("twain:CanoScan", target, dpi=300),
                             target)
            command = calls[0]
            self.assertIn("--driver", command)
            self.assertIn("--dpi", command)
            self.assertIn("300", command)


if __name__ == "__main__":
    unittest.main(verbosity=2)
