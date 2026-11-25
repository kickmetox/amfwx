"""PDF merge/split tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (AppConfig, images_to_pdf, merge_pdfs, pdf_extract_text,
                   split_pdf)


@unittest.skipUnless(__import__("importlib").util.find_spec("pymupdf")
                     or __import__("importlib").util.find_spec("fitz"),
                     "PyMuPDF fehlt")
class PdfToolTests(unittest.TestCase):
    def _pdf(self, folder, name, color):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow fehlt")
        image = Path(folder) / f"{name}.jpg"
        Image.new("RGB", (80, 100), color).save(image, "JPEG")
        target = Path(folder) / f"{name}.pdf"
        images_to_pdf([image], target)
        return target

    def test_merge_and_split(self):
        with tempfile.TemporaryDirectory() as folder:
            first = self._pdf(folder, "a", "white")
            second = self._pdf(folder, "b", "gray")
            merged = Path(folder) / "merged.pdf"
            merge_pdfs([first, second], merged)
            pages = Path(folder) / "pages"
            outputs = split_pdf(merged, pages)
            self.assertEqual(len(outputs), 2)
            self.assertIn("", pdf_extract_text(merged))

    def test_cli(self):
        config = AppConfig.parse(["--pdf-merge", "out.pdf",
                                  "--pdf-input", "a.pdf",
                                  "--pdf-input", "b.pdf"])
        self.assertEqual(config.pdf_inputs, ["a.pdf", "b.pdf"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
