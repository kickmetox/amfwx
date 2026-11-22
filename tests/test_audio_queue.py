"""Audio queue tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.audio import AudioQueuePlayer


class AudioQueueTests(unittest.TestCase):
    def test_feed_and_wait(self):
        try:
            player = AudioQueuePlayer(1, 8000, 16)
        except OSError as error:
            self.skipTest(f"waveOut nicht verfügbar: {error}")
        try:
            player.feed(b"\x00\x00" * 400)
            player.feed(b"\x00\x00" * 400)
            player.wait()
        finally:
            player.stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)
