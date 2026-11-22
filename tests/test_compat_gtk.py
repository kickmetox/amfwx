"""GTK compatibility tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.compat import gtk as Gtk


class GtkCompatTests(unittest.TestCase):
    def test_window_box_button(self):
        app = Gtk.Application()
        window = Gtk.ApplicationWindow(application=app, title="Demo")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        window.set_child(box)
        clicked = []
        label = Gtk.Label(label="Hallo")
        button = Gtk.Button(label="OK")
        button.connect("clicked", lambda _button: clicked.append(1))
        box.append(label)
        box.append(button)
        button.widget.activate()
        self.assertEqual(clicked, [1])
        self.assertEqual(label.get_label(), "Hallo")
        window.close()

    def test_controls(self):
        app = Gtk.Application()
        window = Gtk.ApplicationWindow(application=app, title="Controls")
        box = Gtk.Box()
        window.set_child(box)
        entry = Gtk.Entry("start")
        entry.set_text("neu")
        self.assertEqual(entry.get_text(), "neu")
        check = Gtk.CheckButton("Aktiv")
        check.set_active(True)
        self.assertTrue(check.get_active())
        switch = Gtk.Switch()
        switch.set_active(True)
        self.assertTrue(switch.get_active())
        scale = Gtk.Scale()
        scale.set_value(42)
        self.assertEqual(scale.get_value(), 42.0)
        progress = Gtk.ProgressBar()
        progress.set_fraction(0.5)
        self.assertEqual(progress.widget.value(), 50)
        window.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
