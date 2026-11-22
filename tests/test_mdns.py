"""mDNS/DNS-SD tests."""

from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import build_query, decode_name, encode_name, parse_packet
from amfwx.mdns import TYPE_PTR


class MdnsTests(unittest.TestCase):
    def test_query(self):
        query = build_query("_http._tcp.local")
        self.assertEqual(query[4:6], b"\x00\x01")
        self.assertEqual(query[-4:], b"\x00\x0c\x00\x01")

    def test_response_parse(self):
        target = encode_name("printer._http._tcp.local")
        rdata = target
        name = encode_name("_http._tcp.local")
        answer = (name + struct.pack(">HHIH", TYPE_PTR, 1, 120, len(rdata)) +
                  rdata)
        packet = struct.pack(">HHHHHH", 0, 0x8400, 0, 1, 0, 0) + answer
        records = parse_packet(packet)
        self.assertEqual(records[0]["type"], TYPE_PTR)
        self.assertEqual(records[0]["value"], "printer._http._tcp.local")

    def test_compression(self):
        data = encode_name("local") + b"\xc0\x00"
        name, end = decode_name(data, 0)
        self.assertEqual(name, "local")
        self.assertEqual(end, 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
