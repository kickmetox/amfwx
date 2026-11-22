"""DSP layer tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (AudioBuffer, Biquad, DspGraph, Gain, Mixer, Plugin,
                   PluginError, PluginRegistry)


class DspTests(unittest.TestCase):
    def test_gain_and_mix(self):
        first = AudioBuffer(1, 8000, 3)
        first.data = [[1.0, 2.0, 3.0]]
        second = AudioBuffer(1, 8000, 3)
        second.data = [[0.5, 0.5, 0.5]]
        Gain(2.0).process(first)
        self.assertEqual(first.data[0], [2.0, 4.0, 6.0])
        mixed = Mixer([0.5, 0.5]).process([first, second])
        self.assertEqual(mixed.data[0], [1.25, 2.25, 3.25])

    def test_biquad(self):
        buffer = AudioBuffer(1, 48000, 4800)
        for index in range(4800):
            buffer.data[0][index] = 1.0 if index == 0 else 0.0
        filtered = Biquad(48000, 1000, kind="lowpass").process(buffer)
        self.assertTrue(any(abs(value) > 0 for value in filtered.data[0]))
        self.assertLessEqual(max(abs(value) for value in filtered.data[0]),
                             1.0)

    def test_graph(self):
        buffer = AudioBuffer(1, 8000, 3)
        buffer.data = [[1.0, 2.0, 3.0]]
        graph = DspGraph([Gain(0.5), Gain(2.0)])
        self.assertEqual(len(graph), 2)
        graph.process(buffer)
        self.assertEqual(buffer.data[0], [1.0, 2.0, 3.0])


    def test_plugin_registry(self):
        registry = PluginRegistry()

        class Demo(Plugin):
            name = "demo"
            version = "1.0"

        plugin = registry.register(Demo())
        self.assertEqual(registry.names(), ["demo"])
        self.assertIs(registry.get("demo"), plugin)
        with self.assertRaises(PluginError):
            registry.register(Demo())
        registry.unregister("demo")
        self.assertEqual(registry.names(), [])

    def test_plugin_example(self):
        registry = PluginRegistry()
        plugin = registry.load_module("examples.plugins.hello")
        self.assertEqual(plugin.name, "hello")
        registry.activate_all()
        self.assertTrue(plugin.activated)
        registry.deactivate_all()
        self.assertFalse(plugin.activated)


if __name__ == "__main__":
    unittest.main(verbosity=2)
