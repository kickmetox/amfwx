"""Bidi level and reorder tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.bidi import bidi_levels, bidi_reorder


class BidiTests(unittest.TestCase):
    def test_levels(self):
        levels = bidi_levels("abc مرحبا")
        self.assertTrue(levels)
        self.assertEqual(levels[0] % 2, 0)
        self.assertTrue(any(level % 2 for level in levels))

    def test_reorder(self):
        self.assertEqual(bidi_reorder("hello"), "hello")
        mixed = bidi_reorder("abc مرحبا def")
        self.assertNotEqual(mixed, "abc مرحبا def")
        self.assertTrue(mixed.startswith("abc "))
        self.assertTrue(mixed.endswith(" def"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
