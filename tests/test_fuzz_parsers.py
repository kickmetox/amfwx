"""Deterministic parser fuzzing."""

from __future__ import annotations

import os
import random
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import MidiFile, Mp4Info, ResourcePack


class ParserFuzzTests(unittest.TestCase):
    def test_midi_and_mp4_random_bytes(self):
        random.seed(20261122)
        for _ in range(200):
            data = bytes(random.randrange(256) for _ in range(
                random.randrange(0, 96)))
            for parser in (MidiFile, Mp4Info):
                try:
                    parser(data)
                except Exception:
                    pass

    def test_invalid_resource_pack(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "broken.zip")
            with open(path, "wb") as handle:
                handle.write(b"not a zip")
            with self.assertRaises(zipfile.BadZipFile):
                ResourcePack(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
