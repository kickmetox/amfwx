"""CAN tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import CanError, CanFrame, PcanBus


class CanTests(unittest.TestCase):
    def test_frame(self):
        frame = CanFrame(0x123, b"\x01\x02")
        self.assertEqual(frame.identifier, 0x123)
        self.assertEqual(frame.data, b"\x01\x02")
        self.assertTrue(CanFrame(0x1FFFFFFF, b"", extended=True).extended)
        with self.assertRaises(CanError):
            CanFrame(0x800)

    def test_backend_missing(self):
        try:
            bus = PcanBus(library="definitely_missing_pcan.dll")
        except CanError:
            return
        self.assertFalse(bus.initialized)


if __name__ == "__main__":
    unittest.main(verbosity=2)
