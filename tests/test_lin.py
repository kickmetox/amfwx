"""LIN tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import LinError, LinFrame, PcanLin


class LinTests(unittest.TestCase):
    def test_frame(self):
        frame = LinFrame(0x10, b"\x01")
        self.assertEqual(frame.identifier, 0x10)
        self.assertEqual(frame.data, b"\x01")
        with self.assertRaises(LinError):
            LinFrame(0x40, b"\x01")
        with self.assertRaises(LinError):
            LinFrame(0x10, b"")

    def test_backend_missing(self):
        try:
            bus = PcanLin(library="definitely_missing_pcan.dll")
        except LinError:
            return
        self.assertFalse(bus.initialized)


if __name__ == "__main__":
    unittest.main(verbosity=2)
