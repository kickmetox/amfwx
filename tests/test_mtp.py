"""MTP camera tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, list_mtp_devices


class MtpTests(unittest.TestCase):
    def test_list(self):
        self.assertIsInstance(list_mtp_devices(), list)

    def test_cli(self):
        config = AppConfig.parse(["--mtp-download", "D:\\Photos"])
        self.assertEqual(config.mtp_download, "D:\\Photos")
        self.assertTrue(AppConfig.parse(["--list-mtp"]).list_mtp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
