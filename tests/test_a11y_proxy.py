"""Native accessibility proxy tests."""

from __future__ import annotations

import ctypes
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Button, Label, TextEdit, Window
from amfwx.msaa import (do_default_action, read_accessible,
                        read_focus, read_location, read_selection,
                        select_accessible, set_accessible_value)


class AccessibilityProxyTests(unittest.TestCase):
    def test_proxy_windows(self):
        window = Window("A11Y", 400, 300)
        window.root.add(Label("Label"))
        window.root.add(Button("Button"))
        window.root.add(TextEdit("Edit"))
        window._layout_root()
        self.assertEqual(len(window._a11y_windows), 3)
        names = []
        for handle in window._a11y_windows.values():
            buffer = ctypes.create_unicode_buffer(64)
            ctypes.windll.user32.GetWindowTextW(handle, buffer, 64)
            names.append(buffer.value)
        self.assertEqual(sorted(names), ["Button", "Edit", "Label"])
        window.close()
        window.process_events(40)

    def test_proxy_actions(self):
        from amfwx import CheckBox, LineEdit
        clicked = []
        checked = []
        window = Window("Actions", 400, 300)
        button = Button("Klick", on_click=lambda: clicked.append(1))
        check = CheckBox("An", on_change=lambda value: checked.append(value))
        edit = LineEdit("alt")
        window.root.add(button)
        window.root.add(check)
        window.root.add(edit)
        window._layout_root()
        handles = {handle: widget for handle, widget in
                   window._a11y_by_handle.items()}
        button_handle = next(handle for handle, widget in handles.items()
                             if widget is button)
        check_handle = next(handle for handle, widget in handles.items()
                            if widget is check)
        edit_handle = next(handle for handle, widget in handles.items()
                           if widget is edit)
        ctypes.windll.user32.SendMessageW(button_handle, 0x00F5, 0, 0)  # BM_CLICK
        self.assertEqual(clicked, [1])
        ctypes.windll.user32.SendMessageW(check_handle, 0x00F5, 0, 0)
        self.assertTrue(check.checked)
        ctypes.windll.user32.SetWindowTextW(edit_handle, "neu")
        window.process_events(20)
        self.assertEqual(edit.text(), "neu")
        window.close()
        window.process_events(40)

    def test_msaa_roles(self):
        from amfwx import CheckBox, LineEdit
        window = Window("MSAA", 400, 300)
        button = Button("Aktion")
        check = CheckBox("An")
        edit = LineEdit("Text")
        window.root.add(button)
        window.root.add(check)
        window.root.add(edit)
        window._layout_root()
        handles = {widget: handle for handle, widget in
                   window._a11y_by_handle.items()}
        button_info = read_accessible(handles[button])
        self.assertEqual(button_info["name"], "Aktion")
        self.assertEqual(button_info["role"], 43)
        edit_info = read_accessible(handles[edit])
        self.assertIn(edit_info["role"], (40, 42))
        window.close()
        window.process_events(40)

    def test_msaa_default_action(self):
        clicked = []
        window = Window("MSAA Action", 400, 300)
        button = Button("Aktion", on_click=lambda: clicked.append(1))
        window.root.add(button)
        window._layout_root()
        handle = window._a11y_windows[id(button)]
        self.assertEqual(do_default_action(handle), 0)
        window.process_events(200)
        self.assertEqual(clicked, [1])
        window.close()
        window.process_events(40)

    def test_msaa_value_and_state(self):
        from amfwx import CheckBox, LineEdit
        window = Window("MSAA State", 400, 300)
        check = CheckBox("An")
        edit = LineEdit("Text")
        window.root.add(check)
        window.root.add(edit)
        window._layout_root()
        check_info = read_accessible(window._a11y_windows[id(check)])
        self.assertEqual(check_info["role"], 44)
        edit_info = read_accessible(window._a11y_windows[id(edit)])
        self.assertEqual(edit_info["value"], "Text")
        window.close()
        window.process_events(40)

    def test_msaa_set_value(self):
        from amfwx import LineEdit
        window = Window("MSAA SetValue", 400, 300)
        edit = LineEdit("alt")
        window.root.add(edit)
        window._layout_root()
        handle = window._a11y_windows[id(edit)]
        self.assertEqual(set_accessible_value(handle, "neu"), 0)
        window.process_events(200)
        self.assertEqual(edit.text(), "neu")
        window.close()
        window.process_events(40)

    def test_msaa_select(self):
        window = Window("MSAA Select", 400, 300)
        button = Button("Aktion")
        window.root.add(button)
        window._layout_root()
        handle = window._a11y_windows[id(button)]
        self.assertEqual(select_accessible(handle), 0)
        window.process_events(80)
        window.close()
        window.process_events(40)

    def test_msaa_focus_read(self):
        window = Window("MSAA Focus", 400, 300)
        button = Button("Aktion")
        window.root.add(button)
        window._layout_root()
        handle = window._a11y_windows[id(button)]
        self.assertEqual(select_accessible(handle), 0)
        window.process_events(100)
        focus = read_focus(handle)
        self.assertEqual(focus["hr"], 0)
        self.assertEqual(focus["vt"], 3)
        window.close()
        window.process_events(40)

    def test_msaa_selection(self):
        window = Window("MSAA Selection", 400, 300)
        button = Button("Aktion")
        window.root.add(button)
        window._layout_root()
        handle = window._a11y_windows[id(button)]
        info = read_selection(handle)
        self.assertIn(info["hr"], (0, 1))
        window.close()
        window.process_events(40)

    def test_msaa_location(self):
        window = Window("MSAA Location", 400, 300)
        button = Button("Aktion")
        window.root.add(button)
        window._layout_root()
        info = read_location(window._a11y_windows[id(button)])
        self.assertEqual(info["hr"], 0)
        self.assertEqual(info["width"], 1)
        self.assertEqual(info["height"], 1)
        window.close()
        window.process_events(40)

    def test_keyboard_tab_navigation(self):
        window = Window("Tab", 400, 300)
        first = Button("Eins")
        second = Button("Zwei")
        window.root.add(first)
        window.root.add(second)
        window._layout_root()
        window._sync_a11y()
        user32 = ctypes.windll.user32
        first_handle = window._a11y_windows[id(first)]
        second_handle = window._a11y_windows[id(second)]
        user32.SetForegroundWindow(ctypes.c_void_p(window.hwnd))
        window.process_events(60)
        user32.SetFocus(ctypes.c_void_p(first_handle))
        user32.SendMessageW(ctypes.c_void_p(first_handle), 0x0100, 0x09, 0)
        window.process_events(60)
        self.assertEqual(user32.GetFocus(), second_handle)
        window.close()
        window.process_events(40)

    def test_missing_uia_provider(self):
        import amfwx.uia_native as native
        old = native._library
        native._library = lambda: (_ for _ in ()).throw(
            OSError("missing uia_provider.dll"))
        try:
            window = Window("No UIA", 400, 300)
            button = Button("Aktion")
            window.root.add(button)
            window._layout_root()
            self.assertEqual(len(window._a11y_windows), 1)
            window.close()
            window.process_events(40)
        finally:
            native._library = old


if __name__ == "__main__":
    unittest.main(verbosity=2)
