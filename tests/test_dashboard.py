from __future__ import annotations
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import AppConfig, DashboardWindow

class DashboardTests(unittest.TestCase):
    def test_window(self):
        window=DashboardWindow()
        try:
            self.assertEqual(window.category.current_text(), 'Alle')
            self.assertTrue(window.refresh_button.text)
        finally:
            window.close()
    def test_cli(self):
        self.assertTrue(AppConfig.parse(['--dashboard']).dashboard)

if __name__ == '__main__':
    unittest.main(verbosity=2)
