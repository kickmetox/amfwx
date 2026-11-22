"""Deterministic media/shader fuzzing."""

from __future__ import annotations

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.audio import decode_wav
from amfwx.shaders import compile_hlsl
from amfwx.video import AviVideo


class MediaFuzzTests(unittest.TestCase):
    def test_avi_and_wav(self):
        random.seed(20261125)
        for _ in range(200):
            data = bytes(random.randrange(256) for _ in range(
                random.randrange(0, 160)))
            for parser in (AviVideo, decode_wav):
                try:
                    parser(data)
                except Exception:
                    pass

    def test_shader_parser(self):
        random.seed(20261126)
        for _ in range(20):
            source = "// " + "".join(
                chr(random.randrange(32, 126)) for _ in range(64))
            try:
                compile_hlsl(source)
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
