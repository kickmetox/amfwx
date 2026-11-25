"""32-bit TWAIN bridge tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import list_twain32_sources
from amfwx.twain32 import Twain32Error, available


class Twain32Tests(unittest.TestCase):
    def test_available(self):
        if not available():
            self.skipTest("kein 32-Bit-Python / Helper")
        self.assertTrue(available())

    def test_sources(self):
        if not available():
            self.skipTest("kein 32-Bit-Python / Helper")
        try:
            sources = list_twain32_sources()
        except Exception as error:
            self.skipTest(f"keine TWAIN-Quellen: {error}")
        self.assertIsInstance(sources, list)
        for source in sources:
            self.assertTrue(source.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
