"""Declarative QuickView tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.quick import QuickView, State, Text


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
