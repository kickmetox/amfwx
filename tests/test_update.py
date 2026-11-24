from __future__ import annotations
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import AppConfig, is_newer, pick_installer

class UpdateTests(unittest.TestCase):
    def test_versions(self):
        self.assertTrue(is_newer('5.31.0','5.30.0'))
        self.assertFalse(is_newer('5.30.0','5.30.0'))
    def test_installer_and_cli(self):
        self.assertEqual(pick_installer([{'name':'AMFWX-Own-Setup-5.30.0.exe','url':'x'}]),'x')
        self.assertTrue(AppConfig.parse(['--check-update']).check_update)

if __name__ == '__main__':
    unittest.main(verbosity=2)
