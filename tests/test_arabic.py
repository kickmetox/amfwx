"""Arabic joining tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.arabic import arabic_shape


class ArabicTests(unittest.TestCase):
    def test_joining_forms(self):
        shaped = arabic_shape("سلام")
        self.assertTrue(all(ord(character) >= 0xFE70 for character in shaped))
        self.assertNotEqual(shaped, "سلام")

    def test_lam_alef(self):
        self.assertEqual(arabic_shape("لا"), "\uFEFB")
        self.assertEqual(arabic_shape("بلا")[-1], "\uFEFC")

    def test_latin_untouched(self):
        self.assertEqual(arabic_shape("hello"), "hello")


if __name__ == "__main__":
    unittest.main(verbosity=2)
