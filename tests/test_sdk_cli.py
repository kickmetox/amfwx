from __future__ import annotations
import contextlib, io, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx.sdk import main

class SdkCliTests(unittest.TestCase):
    def test_tools(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(['--tools']),0)
        self.assertIn('create_window', output.getvalue())
    def test_version(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(['--version']),0)
        self.assertTrue(output.getvalue().strip())

if __name__ == '__main__':
    unittest.main(verbosity=2)
