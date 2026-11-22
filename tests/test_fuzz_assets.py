"""Deterministic asset-parser fuzzing."""

from __future__ import annotations

import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.png import decode_png
from amfwx.webp import decode_webp


class AssetFuzzTests(unittest.TestCase):
    def test_png_and_webp_random_bytes(self):
        random.seed(20261123)
        for _ in range(200):
            data = bytes(random.randrange(256) for _ in range(
                random.randrange(0, 128)))
            for parser in (decode_png, decode_webp):
                try:
                    parser(data)
                except Exception:
                    pass

    def test_truetype_random_bytes(self):
        from amfwx.font import TrueTypeFont
        random.seed(20261124)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "broken.ttf")
            for _ in range(50):
                with open(path, "wb") as handle:
                    handle.write(bytes(random.randrange(256) for _ in range(
                        random.randrange(0, 256))))
                try:
                    TrueTypeFont(path, 16)
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
