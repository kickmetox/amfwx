"""Tkinter compatibility tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.compat import tkinter as tk


class TkCompatTests(unittest.TestCase):
    def test_pack_and_button(self):
        root = tk.Tk()
        clicked = []
        try:
            tk.Label(root, text="Hallo").pack()
            button = tk.Button(root, text="OK",
                               command=lambda: clicked.append(1))
            button.pack()
            button.widget.activate()
            self.assertEqual(clicked, [1])
            root.update()
        finally:
            root.destroy()

    def test_entry_variable(self):
        root = tk.Tk()
        try:
            value = tk.StringVar("start")
            entry = tk.Entry(root, textvariable=value)
            entry.pack()
            self.assertEqual(entry.get(), "start")
            value.set("neu")
            self.assertEqual(entry.get(), "neu")
            entry.insert(0, "!")
            self.assertIn("!", entry.get())
        finally:
            root.destroy()

    def test_frame_and_checkbutton(self):
        root = tk.Tk()
        try:
            frame = tk.Frame(root)
            frame.pack()
            variable = tk.BooleanVar(False)
            check = tk.Checkbutton(frame, text="Aktiv", variable=variable)
            check.pack()
            check.invoke()
            self.assertTrue(variable.get())
            root.update()
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
