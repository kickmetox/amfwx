"""EtherNet/IP ListIdentity tests."""

from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import parse_enip_response
from amfwx.enip import ITEM_LIST_IDENTITY, LIST_IDENTITY, parse_response


def response():
    item = struct.pack("<H", 1)
    item += struct.pack(">HH", 2, 44818)
    item += bytes([192, 168, 1, 10])
    item += b"\x00" * 8
    item += struct.pack("<HHHHHI", 1, 12, 100, 0x0102, 0, 1234)
    name = b"Test"
    item += bytes([len(name)]) + name + bytes([3])
    payload = struct.pack("<H", 1)
    payload += struct.pack("<HH", ITEM_LIST_IDENTITY, len(item)) + item
    return struct.pack("<HHII8sI", LIST_IDENTITY, len(payload), 0, 0,
                       b"\x00" * 8, 0) + payload


class EnipTests(unittest.TestCase):
    def test_parse(self):
        devices = parse_response(response(), "10.0.0.1")
        self.assertEqual(len(devices), 1)
        device = devices[0]
        self.assertEqual(device.product_name, "Test")
        self.assertEqual(device.vendor_id, 1)
        self.assertEqual(device.host, "192.168.1.10")
        self.assertEqual(device.port, 44818)

    def test_bad_packet(self):
        with self.assertRaises(Exception):
            parse_response(b"short")


if __name__ == "__main__":
    unittest.main(verbosity=2)
