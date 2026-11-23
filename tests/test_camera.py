"""Camera/chroma tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise unittest.SkipTest("Pillow fehlt")

from amfwx import CameraInfo, chroma_key, composite, list_cameras, list_pnp_cameras


class CameraTests(unittest.TestCase):
    def test_list(self):
        self.assertIsInstance(list_cameras(2), list)
        self.assertEqual(CameraInfo(3).name, "Camera 3")
        self.assertIsInstance(list_pnp_cameras(), list)

    def test_chroma_key(self):
        image = Image.new("RGB", (100, 100), (0, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((30, 30, 70, 70), fill=(220, 20, 20))
        result = chroma_key(image, (0, 255, 0), tolerance=40)
        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(result.getpixel((0, 0))[3], 0)
        self.assertEqual(result.getpixel((50, 50))[3], 255)
        background = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
        merged = composite(result, background)
        self.assertEqual(merged.getpixel((0, 0))[:3], (0, 0, 255))


if __name__ == "__main__":
    unittest.main(verbosity=2)
