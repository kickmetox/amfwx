"""Tray icon test."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import TrayIcon, Window


class TrayTests(unittest.TestCase):
    def test_add_remove(self):
        window = Window("Tray", 200, 100)
        tray = TrayIcon(window, "AMFWX Test")
        try:
            self.assertTrue(tray.add())
            self.assertTrue(tray.visible)
            tray.set_tooltip("Neu")
            self.assertEqual(tray.tooltip, "Neu")
            self.assertTrue(tray.notify("AMFWX", "Bereit"))
            tray.remove()
            self.assertFalse(tray.visible)
        finally:
            tray.remove()
            window.close()
            window.process_events(40)

    def test_notify(self):
        window = Window("Tray", 200, 100)
        tray = TrayIcon(window)
        try:
            self.assertTrue(tray.add())
            self.assertTrue(tray.notify("AMFWX", "Bereit"))
        finally:
            tray.remove()
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
