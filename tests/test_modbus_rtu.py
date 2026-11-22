"""Modbus RTU tests."""

from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.io import ModbusRTU, ModbusRTUError, crc16


class FakeTransport:
    def __init__(self, response):
        self.response = bytearray(response)
        self.written = bytearray()

    def write(self, data):
        self.written.extend(data)

    def read(self, size):
        data = bytes(self.response[:size])
        del self.response[:size]
        return data


def frame(body):
    return body + struct.pack("<H", crc16(body))


class ModbusRTUTests(unittest.TestCase):
    def test_crc(self):
        self.assertEqual(crc16(b"\x01\x03\x00\x00\x00\x02"), 0x0BC4)

    def test_read_registers(self):
        transport = FakeTransport(frame(bytes([1, 3, 4, 0x12, 0x34, 0x56, 0x78])))
        client = ModbusRTU(transport=transport, unit=1)
        self.assertEqual(client.read_holding_registers(0, 2), [0x1234, 0x5678])
        self.assertTrue(transport.written)

    def test_exception(self):
        transport = FakeTransport(frame(bytes([1, 0x83, 2])))
        client = ModbusRTU(transport=transport, unit=1)
        with self.assertRaises(ModbusRTUError):
            client.read_holding_registers(0, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
