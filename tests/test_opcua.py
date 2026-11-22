"""Optional OPC UA tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import OpcUaClient, OpcUaError


class OpcUaTests(unittest.TestCase):
    def test_optional_backend(self):
        try:
            import asyncua  # noqa: F401
        except ImportError:
            with self.assertRaises(OpcUaError):
                OpcUaClient("opc.tcp://127.0.0.1:4840").connect()
            return
        self.skipTest("asyncua vorhanden, kein OPC-UA-Server im Test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
