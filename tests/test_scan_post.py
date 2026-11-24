"""Scanner post-processing tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import crop_white, is_blank, postprocess, postprocess_pages


@unittest.skipUnless(__import__("importlib").util.find_spec("PIL"),
                     "Pillow fehlt")
class ScanPostTests(unittest.TestCase):
    def test_blank(self):
        from PIL import Image
        self.assertTrue(is_blank(Image.new("RGB", (100, 100), "white")))
        dark = Image.new("RGB", (100, 100), "white")
        dark.paste((0, 0, 0), (20, 20, 80, 80))
        self.assertFalse(is_blank(dark))

    def test_crop(self):
        from PIL import Image
        image = Image.new("RGB", (300, 300), "white")
        image.paste((0, 0, 0), (100, 100, 200, 200))
        result = crop_white(image)
        self.assertLess(result.width, 300)
        self.assertLess(result.height, 300)

    def test_pipeline_files(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / "blank.jpg"
            second = Path(folder) / "text.jpg"
            Image.new("RGB", (200, 200), "white").save(first)
            image = Image.new("RGB", (200, 200), "white")
            image.paste((0, 0, 0), (50, 50, 150, 150))
            image.save(second)
            pages = postprocess_pages([str(first), str(second)],
                                      drop_blank=True)
            self.assertEqual(len(pages), 1)
            self.assertTrue(Path(pages[0]).is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
