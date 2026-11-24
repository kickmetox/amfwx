"""OCR tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, ocr_available, ocr_image


@unittest.skipUnless(ocr_available(), "winsdk fehlt")
class OcrTests(unittest.TestCase):
    def test_image(self):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            self.skipTest("Pillow fehlt")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ocr.png"
            image = Image.new("RGB", (700, 160), "white")
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 48)
            draw.text((20, 40), "AMFWX OCR Test 123", font=font,
                      fill="black")
            image.save(path)
            text = ocr_image(path)
            self.assertIn("AMFWX", text)

    def test_cli(self):
        self.assertEqual(AppConfig.parse(["--ocr-image", "x"]).ocr_image, "x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
