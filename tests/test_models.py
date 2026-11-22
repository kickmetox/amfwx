"""Model layer tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import ListModel, SortFilterModel, TableModel


class ModelTests(unittest.TestCase):
    def test_list_model(self):
        changes = []
        model = ListModel(["b", "a"])
        model.connect(lambda _model: changes.append(1))
        model.append("c")
        model.sort()
        self.assertEqual([model.data(i) for i in range(3)],
                         ["a", "b", "c"])
        self.assertTrue(model.remove(0))
        self.assertEqual(model.data(0), "b")
        self.assertTrue(changes)

    def test_table_and_filter(self):
        model = TableModel(["Name", "Größe"], [["b", 2], ["a", 1]])
        model.sort(0)
        self.assertEqual(model.data(0, 0), "a")
        self.assertTrue(model.set_data(0, 1, 7))
        self.assertEqual(model.data(0, 1), 7)
        filtered = SortFilterModel(model, 0, "b")
        self.assertEqual(filtered.row_count(), 1)
        self.assertEqual(filtered.data(0, 0), "b")
        model.append_row(["c", 3])
        self.assertEqual(filtered.row_count(), 1)
        filtered.set_query("c")
        self.assertEqual(filtered.data(0, 0), "c")


if __name__ == "__main__":
    unittest.main(verbosity=2)
