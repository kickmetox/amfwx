"""Mixer UI tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import MixerPanel, MixerStrip, Rect, Settings


class MixerTests(unittest.TestCase):
    def test_layout(self):
        panel = MixerPanel([MixerStrip("A"), MixerStrip("B")])
        panel.arrange(Rect(0, 0, 200, 100))
        self.assertEqual(len(panel.strips), 2)
        self.assertEqual(panel.strips[0].rect.w, 96)
        self.assertEqual(panel.strips[1].rect.x, 100)
        self.assertEqual(panel.strips[0].slider.rect.w, 88)
        panel.strips[0].apply_state({"gain": 0.5})
        self.assertEqual(panel.state()["A"], 0.5)
        panel.apply_state({"A": 1.0, "B": 0.25})
        self.assertEqual(panel.strips[1].gain, 0.25)

    def test_settings_preset(self):
        import tempfile
        panel = MixerPanel([MixerStrip("A"), MixerStrip("B")])
        panel.apply_state({"A": 0.5, "B": 0.25})
        with tempfile.TemporaryDirectory() as folder:
            settings = Settings(os.path.join(folder, "settings.json"))
            panel.save_presets(settings)
            restored = MixerPanel([MixerStrip("A"), MixerStrip("B")])
            restored.load_presets(settings)
            self.assertEqual(restored.state(), {"A": 0.5, "B": 0.25})
            file_path = os.path.join(folder, "mix.json")
            panel.save_file(file_path)
            loaded = MixerPanel([MixerStrip("A"), MixerStrip("B")])
            loaded.load_file(file_path)
            self.assertEqual(loaded.state(), {"A": 0.5, "B": 0.25})


if __name__ == "__main__":
    unittest.main(verbosity=2)
