"""RichText tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Canvas, Rect, RichDocument, RichText


class RichTextTests(unittest.TestCase):
    def test_plain_text(self):
        document = RichDocument(
            '<h1>Titel</h1><p>Hallo <b>Welt</b> '
            '<a href="https://example.com">Link</a></p>')
        self.assertIn("Titel", document.plain_text())
        self.assertIn("Hallo Welt Link", document.plain_text())

    def test_render(self):
        widget = RichText("<p>Ein <b>fetter</b> Satz mit "
                          "<a href='#x'>Link</a>.</p>")
        widget.arrange(Rect(0, 0, 300, 120))
        canvas = Canvas(300, 120)
        widget.paint(canvas)
        self.assertEqual(widget.size_hint(), (360, 120))


if __name__ == "__main__":
    unittest.main(verbosity=2)
