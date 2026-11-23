"""Windows printer tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, list_printers


class WinPrintTests(unittest.TestCase):
    def test_list(self):
        printers = list_printers()
        self.assertIsInstance(printers, list)
        for printer in printers:
            self.assertTrue(printer.name)

    def test_cli(self):
        self.assertTrue(AppConfig.parse(["--list-printers"]).list_printers)
        config = AppConfig.parse(["--print-file", "x.pdf",
                                  "--printer", "Kyocera"])
        self.assertEqual(config.printer, "Kyocera")


if __name__ == "__main__":
    unittest.main(verbosity=2)
