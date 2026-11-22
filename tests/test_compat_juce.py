"""JUCE compatibility tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.compat import juce


class JuceCompatTests(unittest.TestCase):
    def test_window_and_button(self):
        window = juce.DocumentWindow("Demo")
        label = juce.Label("label", "Hallo")
        window.setContentOwned(label)
        clicked = []
        button = juce.TextButton("button", "OK")
        button.onClick(lambda: clicked.append(1))
        window.addAndMakeVisible(button)
        button.triggerClick()
        self.assertEqual(clicked, [1])
        self.assertEqual(label.getText(), "Hallo")
        window.closeButtonPressed()

    def test_controls(self):
        slider = juce.Slider("gain")
        slider.setRange(0, 10)
        slider.setValue(7)
        self.assertEqual(slider.getValue(), 7.0)
        combo = juce.ComboBox("items")
        combo.addItem("A")
        combo.addItem("B")
        combo.setSelectedItemIndex(1)
        self.assertEqual(combo.getSelectedItemIndex(), 1)
        toggle = juce.ToggleButton("toggle", "Aktiv")
        toggle.setToggleState(True)
        self.assertTrue(toggle.getToggleState())
        editor = juce.TextEditor("text")
        editor.setText("neu")
        self.assertEqual(editor.getText(), "neu")


if __name__ == "__main__":
    unittest.main(verbosity=2)
