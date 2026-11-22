"""MIDI parser tests."""

from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import MidiFile


def midi_file():
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480)
    track = (b"\x00\x90\x3c\x64" +
             b"\x83\x60\x80\x3c\x00" +
             b"\x00\xff\x2f\x00")
    return header + b"MTrk" + struct.pack(">I", len(track)) + track


class MidiTests(unittest.TestCase):
    def test_note_parse(self):
        midi = MidiFile(midi_file())
        self.assertEqual(midi.format, 0)
        self.assertEqual(midi.division, 480)
        self.assertEqual(len(midi.notes), 1)
        note = midi.notes[0]
        self.assertEqual(note.pitch, 60)
        self.assertEqual(note.velocity, 100)
        self.assertAlmostEqual(note.start, 0.0)
        self.assertAlmostEqual(note.duration, 0.5, places=3)
        self.assertAlmostEqual(midi.duration, 0.5, places=3)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            MidiFile(b"not midi")


if __name__ == "__main__":
    unittest.main(verbosity=2)
