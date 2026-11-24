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

    def test_batch(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow fehlt")

        def runner(command, **kwargs):
            target = Path(command[command.index("-o") + 1])
            first = Image.new("RGB", (60, 80), "white")
            second = Image.new("RGB", (60, 80), "gray")
            first.save(target, "TIFF", save_all=True,
                       append_images=[second])
            return Result()

        with tempfile.TemporaryDirectory() as folder:
            scanner = Naps2Scanner(exe="fake.exe", runner=runner)
            pages = scanner.scan_batch("twain:CanoScan", folder, dpi=200)
            self.assertEqual(len(pages), 2)
            self.assertTrue(all(Path(page).is_file() for page in pages))


if __name__ == "__main__":
    unittest.main(verbosity=2)
