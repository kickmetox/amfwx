"""Experimental S7comm packet tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.s7 import (AREA_DB, S7Client, S7Error, build_read, build_setup,
                      build_write)


class S7Tests(unittest.TestCase):
    def test_packets(self):
        setup = build_setup()
        self.assertEqual(setup[0:4], b"\x03\x00\x00\x19")
        self.assertEqual(setup[7:9], b"\x32\x01")
        read = build_read(AREA_DB, 1, 0, 4)
        self.assertEqual(read[0:4], b"\x03\x00\x00\x1f")
        self.assertEqual(read[7:9], b"\x32\x01")
        write = build_write(AREA_DB, 1, 0, b"\x01\x02")
        self.assertEqual(write[0:4], b"\x03\x00\x00\x25")

    def test_read_write_parse(self):
        client = S7Client("127.0.0.1")
        client._request = lambda _packet: (
            b"", bytes([0xFF, 4, 0, 32, 1, 2, 3, 4]))
        self.assertEqual(client.read_db(1, 0, 4), b"\x01\x02\x03\x04")
        client._request = lambda _packet: (b"", bytes([0xFF]))
        self.assertTrue(client.write_db(1, 0, b"\x01"))

    def test_error(self):
        client = S7Client("127.0.0.1")
        client._request = lambda _packet: (b"", bytes([0x00]))
        with self.assertRaises(S7Error):
            client.read_db(1, 0, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
