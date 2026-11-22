"""wxWidgets compatibility tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.compat import wx


class WxCompatTests(unittest.TestCase):
    def test_frame_panel_sizer(self):
        app = wx.App()
        frame = wx.Frame(None, title="Demo", size=(640, 400))
        panel = wx.Panel(frame)
        sizer = wx.BoxSizer(wx.VERTICAL)
        clicked = []
        label = wx.StaticText(panel, label="Hallo")
        button = wx.Button(panel, label="OK")
        button.Bind(wx.EVT_BUTTON, lambda _event: clicked.append(1))
        sizer.Add(label, 0, wx.ALL, 4)
        sizer.Add(button, 0, wx.ALL, 4)
        panel.SetSizer(sizer)
        frame.Show()
        button.widget.activate()
        self.assertEqual(clicked, [1])
        self.assertEqual(label.widget.text, "Hallo")
        frame.Destroy()

    def test_controls(self):
        app = wx.App()
        frame = wx.Frame(None, title="Controls")
        panel = wx.Panel(frame)
        text = wx.TextCtrl(panel, "start")
        text.SetValue("neu")
        self.assertEqual(text.GetValue(), "neu")
        check = wx.CheckBox(panel, "Aktiv")
        check.SetValue(True)
        self.assertTrue(check.GetValue())
        gauge = wx.Gauge(panel, 100)
        gauge.SetValue(40)
        self.assertEqual(gauge.widget.value(), 40)
        choice = wx.Choice(panel)
        choice.Append("A")
        choice.Append("B")
        choice.SetSelection(1)
        self.assertEqual(choice.GetSelection(), 1)
        frame.Destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
