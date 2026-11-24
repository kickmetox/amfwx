"""Becker Centronic USB tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, BeckerStick, becker_code, becker_parse, list_sticks


class FakeSerial:
    def __init__(self, *args, **kwargs):
        self.written = []

    def write(self, data):
        self.written.append(data)

    def close(self):
        pass


class BeckerTests(unittest.TestCase):
    def test_code(self):
        code = becker_code(1, "1737B", 1, 0x20)
        self.assertEqual(len(code), 42)
        self.assertTrue(code.endswith("B3"))
        packet = becker_parse(b"\x02" + code.encode() + b"\x03")
        self.assertEqual(packet["channel"], 1)
        self.assertEqual(packet["command"], "up")

    def test_send(self):
        serial = FakeSerial()
        stick = BeckerStick("COM9", serial_factory=lambda *a, **k: serial)
        stick.up(1)
        self.assertEqual(len(serial.written), 1)
        self.assertTrue(serial.written[0].startswith(b"\x02"))
        self.assertTrue(serial.written[0].endswith(b"\x03"))
        stick.close()

    def test_cli(self):
        config = AppConfig.parse(["--becker-port", "COM9",
                                  "--becker-action", "up",
                                  "--becker-channel", "2"])
        self.assertEqual(config.becker_channel, 2)
        self.assertIsInstance(list_sticks(), list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
