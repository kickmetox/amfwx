"""Application lifecycle tests."""

from __future__ import annotations

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, Application


class ApplicationTests(unittest.TestCase):
    def test_parse(self):
        config = AppConfig.parse(["--theme", "light", "--title", "Demo",
                                  "--no-single"])
        self.assertEqual(config.theme, "light")
        self.assertEqual(config.title, "Demo")
        self.assertFalse(config.single)
        self.assertIn("--theme", config.usage())

    def test_version(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = Application(AppConfig(show_version=True)).run()
        self.assertEqual(result, 0)
        self.assertIn("AMFWX", output.getvalue())

    def test_demo_window(self):
        from tools.amfwx_app import create_window
        window = create_window(AppConfig(title="Demo", width=320,
                                         height=200))
        try:
            self.assertEqual(window.title, "Demo")
            self.assertGreaterEqual(len(window.root.children), 3)
        finally:
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
