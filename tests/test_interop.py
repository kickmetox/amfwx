"""AMFWX touch, interop, file-dialog imports and reverse bridge."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, r"D:\AI_Temp\AMFW")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Label, Rect, Window
from amfwx.filedialog import open_file, save_file
from amfwx.interop import ThemeTokens, from_amfw, to_amfwx
from amfwx.theme import DARK
from amfwx.touch import GestureRecognizer


class InteropTests(unittest.TestCase):
    def test_gestures(self):
        events = []
        recognizer = GestureRecognizer()
        recognizer.connect(events.append)
        recognizer.touch(1, 10, 10, "down")
        recognizer.touch(1, 11, 11, "up")
        self.assertEqual(events[-1].kind, "tap")
        recognizer.touch(2, 0, 0, "down")
        recognizer.touch(3, 40, 0, "down")
        recognizer.touch(3, 50, 20, "move")
        self.assertTrue(any(event.kind in ("pinch", "rotate", "pan")
                            for event in events))

    def test_theme_interop(self):
        tokens = ThemeTokens()
        theme = to_amfwx(tokens)
        self.assertEqual(theme.background.r, 0x18)
        self.assertEqual(theme.accent.b, 0xF6)
        self.assertEqual(f"#{theme.accent.r:02x}{theme.accent.g:02x}{theme.accent.b:02x}", "#3b82f6")

    def test_window_touch_dispatch(self):
        window = Window("touch", 400, 300)
        label = Label("touch")
        label.arrange(Rect(10, 10, 100, 30))
        window.root.children.clear()
        window.root.add(label)
        window._touch(1, 20, 20, "down")
        window._touch(1, 21, 21, "up")
        window.close()
        window.process_events(40)

    def test_file_dialog_import(self):
        self.assertTrue(callable(open_file))
        self.assertTrue(callable(save_file))

    def test_amfw_theme_conversion(self):
        try:
            from amfw import make_theme
        except Exception:
            self.skipTest("AMFW not available")
        tokens = from_amfw(make_theme("dark"))
        self.assertTrue(tokens.background.startswith("#"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
