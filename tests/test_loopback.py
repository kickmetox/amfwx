"""Loopback serial tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.io import LoopbackSerial


class LoopbackTests(unittest.TestCase):
    def test_pair(self):
        first, second = LoopbackSerial.pair()
        self.assertEqual(first.write(b"ping"), 4)
        self.assertEqual(second.read(4), b"ping")
        self.assertEqual(second.read(4), b"")
        second.write(b"pong")
        self.assertEqual(first.read(4), b"pong")

    def test_flush(self):
        device = LoopbackSerial(echo=True)
        device.write(b"x")
        self.assertEqual(device.read(1), b"x")
        device.flush()
        self.assertEqual(device.read(1), b"")


if __name__ == "__main__":
    unittest.main(verbosity=2)
