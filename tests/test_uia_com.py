"""UIA COM regression tests for the WebGUI internals."""

from __future__ import annotations

import ctypes
import os
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Button, Label, Window
from amfwx.uia_provider import (
    IID_FRAGMENT, IID_ROOT, IID_SIMPLE, UIA_InvokePatternId,
    UIA_NamePropertyId, UIA_TransformPatternId, UiaProvider, VARIANT,
)


class UiaComTests(unittest.TestCase):
    def test_guid_string_and_query_interface(self):
        self.assertEqual(
            str(IID_ROOT), "620ce2a5-ab8f-40a9-86cb-de3c75599b58")
        window = Window("COM", 400, 300)
        button = Button("Aktion")
        window.root.children.clear()
        window.root.add(button)
        provider = UiaProvider(window)
        node = provider.root.children[0]
        for iid in (IID_SIMPLE, IID_FRAGMENT):
            result = ctypes.c_void_p()
            code = node._query(node.simple, ctypes.pointer(iid),
                               ctypes.pointer(result))
            self.assertEqual(code, 0)
            self.assertTrue(result.value)
        window.close()
        window.process_events(40)

    def test_simple_vtable_entries(self):
        window = Window("Simple", 400, 300)
        button = Button("Aktion")
        window.root.children.clear()
        window.root.add(button)
        provider = UiaProvider(window)
        node = provider.root.children[0]
        pattern = ctypes.c_void_p()
        code = node._pattern(node.simple, UIA_InvokePatternId,
                             ctypes.pointer(pattern))
        self.assertEqual(code, 0)
        self.assertTrue(pattern.value)
        value = VARIANT()
        node._property(node.simple, UIA_NamePropertyId,
                        ctypes.pointer(value))
        self.assertTrue(value.vt)
        host = ctypes.c_void_p()
        provider.root._host(provider.root.simple, ctypes.pointer(host))
        self.assertTrue(host.value)
        window.close()
        window.process_events(40)

    def test_transform_pattern(self):
        import ctypes
        window = Window("Transform", 400, 300)
        provider = UiaProvider(window)
        pattern = ctypes.c_void_p()
        provider.root._pattern(provider.root.simple, UIA_TransformPatternId,
                               ctypes.pointer(pattern))
        self.assertTrue(pattern.value)
        can_move = ctypes.c_int()
        provider.root._can_move(provider.root.simple,
                                ctypes.pointer(can_move))
        self.assertEqual(can_move.value, 1)
        window.close()
        window.process_events(40)

    def test_ui_thread_invoke(self):
        window = Window("Invoke", 400, 300)
        result = []

        def worker():
            result.append(window.invoke(lambda: 42))

        thread = threading.Thread(target=worker)
        thread.start()
        deadline = time.monotonic() + 2
        while thread.is_alive() and time.monotonic() < deadline:
            window.process_events(20)
        thread.join(1)
        self.assertEqual(result, [42])
        window.close()
        window.process_events(40)

    def test_msaa_accessible(self):
        from amfwx.msaa import VARIANT
        window = Window("MSAA", 400, 300)
        window.root.add(Label("Hallo"))
        window.root.add(Button("OK"))
        window.enable_msaa()
        accessible = window.msaa
        count = ctypes.c_int()
        accessible._child_count(accessible._interface, ctypes.pointer(count))
        self.assertEqual(count.value, 2)
        child = VARIANT()
        child.vt = 3
        child.value = 1
        name = ctypes.c_void_p()
        accessible._name(accessible._interface, child, ctypes.pointer(name))
        self.assertEqual(ctypes.wstring_at(name.value), "Hallo")
        window.close()
        window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
