"""Texture mipmap tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Color, Texture


class TextureTests(unittest.TestCase):
    def test_mips_and_sampling(self):
        pixels = bytearray()
        for _ in range(16):
            pixels += bytes((0, 0, 255, 255))
        texture = Texture(4, 4, pixels)
        self.assertGreater(len(texture.levels), 1)
        self.assertEqual(texture.levels[-1][0], 1)
        color = texture.sample(0.5, 0.5)
        self.assertGreater(color.r, 200)
        self.assertLess(color.g, 40)

    def test_bilinear_edge(self):
        texture = Texture(2, 2, bytes((0, 0, 0, 255) * 4))
        color = texture.sample(0.0, 0.0)
        self.assertEqual(color, Color(0, 0, 0, 255))


if __name__ == "__main__":
    unittest.main(verbosity=2)
