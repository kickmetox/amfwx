"""Declarative QuickView tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.quick import (ForEach, HStack, ListState, QuickView, State, Text,
                         VStack)


class QuickTests(unittest.TestCase):
    def test_state_rebuild(self):
        state = State("A")
        view = QuickView("Quick", lambda value: [Text(value)], state=state)
        try:
            self.assertEqual(view.root.children[0].text, "A")
            state.set("B")
            self.assertEqual(view.root.children[0].text, "B")
        finally:
            view.dispose()
            view.process_events(40)

    def test_button_updates_state(self):
        state = State(0)

        def build(value):
            return [Text(str(value)),
                    __import__("amfwx").Button(
                        "Plus", on_click=lambda: state.set(state.value + 1))]

        view = QuickView("Counter", build, state=state)
        try:
            view.root.children[1].activate()
            self.assertEqual(state.value, 1)
            self.assertEqual(view.root.children[0].text, "1")
        finally:
            view.dispose()
            view.process_events(40)

    def test_nested_stacks(self):
        root = VStack(Text("A"), HStack(Text("B"), Text("C")))
        view = QuickView("Nested", lambda _value: [root])
        try:
            view._layout_root()
            self.assertGreater(len(root.children), 1)
            self.assertEqual(root.children[1].orientation, "horizontal")
        finally:
            view.dispose()
            view.process_events(40)

    def test_list_state(self):
        state = ListState(["A"])
        view = QuickView("List", lambda items: [ForEach(items, Text)],
                         state=state)
        try:
            self.assertEqual(len(view.root.children[0].children), 1)
            state.append("B")
            self.assertEqual(len(view.root.children[0].children), 2)
        finally:
            view.dispose()
            view.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
