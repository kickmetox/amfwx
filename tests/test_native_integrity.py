"""Native DLL integrity tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.verify_native import verify


class NativeIntegrityTests(unittest.TestCase):
    def test_manifest(self):
        self.assertEqual(verify(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
