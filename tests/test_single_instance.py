"""Single-instance tests."""

from __future__ import annotations

import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import SingleInstance


class SingleInstanceTests(unittest.TestCase):
    def test_mutex(self):
        name = "amfwx-test-mutex"
        first = SingleInstance(name)
        second = SingleInstance(name)
        try:
            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())
            self.assertTrue(second.already_running)
        finally:
            first.release()
            second.release()

    def test_after_release(self):
        name = "amfwx-test-mutex-2"
        first = SingleInstance(name)
        self.assertTrue(first.acquire())
        first.release()
        again = SingleInstance(name)
        self.assertTrue(again.acquire())
        again.release()

    def test_activation(self):
        name = "amfwx-test-mutex-3"
        activated = threading.Event()
        first = SingleInstance(name, on_activate=activated.set)
        second = SingleInstance(name)
        try:
            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())
            self.assertTrue(activated.wait(2.0))
        finally:
            first.release()
            second.release()


if __name__ == "__main__":
    unittest.main(verbosity=2)
