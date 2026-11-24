"""PDF render/print tests (no paper)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import images_to_pdf
from amfwx.pdf_print import _devmode, render_pdf


def available():
    try:
        import pymupdf  # noqa: F401
        return True
    except ImportError:
        try:
            import fitz  # noqa: F401
            return True
        except ImportError:
            return False


@unittest.skipUnless(available(), "pymupdf fehlt")
class PdfPrintTests(unittest.TestCase):
    def test_render(self):
        from tests.test_scan_pdf import JPEG
        with tempfile.TemporaryDirectory() as folder:
            image = Path(folder) / "page.jpg"
            image.write_bytes(JPEG)
            pdf = Path(folder) / "page.pdf"
            images_to_pdf([image], pdf)
            pages = render_pdf(pdf, dpi=72)
            self.assertEqual(len(pages), 1)
            self.assertGreater(pages[0].width, 0)

    def test_devmode(self):
        devmode = _devmode('ECOSYS M5521cdn', 2, True)
        self.assertIsNotNone(devmode)
        self.assertEqual(devmode.contents.dmCopies, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
