"""ttk compatibility tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.compat import tkinter as tk


class TtkCompatTests(unittest.TestCase):
    def test_notebook(self):
        root = tk.Tk()
        try:
            notebook = tk.ttk.Notebook(root)
            first = tk.Frame(notebook)
            second = tk.Frame(notebook)
            notebook.add(first, text="A")
            notebook.add(second, text="B")
            notebook.select(1)
            self.assertEqual(notebook.widget.active, 1)
            self.assertEqual(notebook.index(second), 1)
        finally:
            root.destroy()

    def test_tree_and_controls(self):
        root = tk.Tk()
        try:
            tree = tk.ttk.Treeview(root, columns=("name",))
            item = tree.insert("", "end", text="Eintrag")
            self.assertEqual(len(tree.widget.items), 1)
            self.assertTrue(tree.delete(item))
            progress = tk.ttk.Progressbar(root, value=25)
            progress.configure(value=60)
            self.assertEqual(progress.widget.value(), 60)
            combo = tk.ttk.Combobox(root, values=["A", "B"])
            combo.set("B")
            self.assertEqual(combo.get(), "B")
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
