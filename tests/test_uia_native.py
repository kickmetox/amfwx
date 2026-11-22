"""Native UIA provider binding tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Button, Window
from amfwx.uia_native import (attach, detach, notify_focus, notify_name,
                             notify_structure, set_bounds, set_name)


class NativeUiaTests(unittest.TestCase):
    def test_attach_and_name(self):
        window = Window("UIA Native", 400, 300)
        button = Button("Aktion")
        window.root.add(button)
        window._layout_root()
        window._sync_a11y()
        handle = window._a11y_windows[id(button)]
        self.assertIn(int(handle), window._uia_native)
        self.assertEqual(set_name(handle, "Neu"), 1)
        self.assertEqual(set_bounds(handle, 10, 20, 220, 32), 1)
        self.assertEqual(notify_focus(handle), 1)
        self.assertEqual(notify_structure(handle), 1)
        self.assertEqual(notify_name(handle, "Alt", "Neu"), 1)
        self.assertEqual(detach(handle), 1)
        window.close()
        window.process_events(40)
