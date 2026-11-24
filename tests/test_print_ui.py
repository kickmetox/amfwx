from __future__ import annotations
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import AppConfig, PrintPreviewWindow

class PrintUiTests(unittest.TestCase):
    def test_window(self):
        window=PrintPreviewWindow()
        try:
            self.assertEqual(window.paper.current_text(), 'A4')
            self.assertEqual(window.copies.text(), '1')
        finally:
            window.close()
    def test_cli(self):
        self.assertEqual(AppConfig.parse(['--print-preview','a.pdf']).print_preview,'a.pdf')

if __name__ == '__main__':
    unittest.main(verbosity=2)
