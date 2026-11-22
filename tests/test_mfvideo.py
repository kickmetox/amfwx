"""Media Foundation H.264/MP4 decode test."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (Canvas, MediaAudio, MediaAudioStream, MediaPlayer,
                   MediaStream, MediaVideo, VideoView)
from amfwx.mfvideo import probe_media_foundation

SAMPLE = Path(r"C:\Users\Lenovo\Desktop\Demo2.mp4")


class MediaFoundationTests(unittest.TestCase):
    def test_library_available(self):
        self.assertTrue(probe_media_foundation())

    def test_decode_sample(self):
        if not SAMPLE.exists():
            self.skipTest("Demo2.mp4 fehlt")
        video = MediaVideo.from_file(SAMPLE)
        canvas = video.frame(0)
        self.assertGreater(canvas.width, 0)
        self.assertGreater(canvas.height, 0)
        self.assertEqual(len(canvas.data), canvas.width * canvas.height * 4)

    def test_video_view(self):
        if not SAMPLE.exists():
            self.skipTest("Demo2.mp4 fehlt")
        view = VideoView(MediaVideo.from_file(SAMPLE))
        view.arrange(__import__("amfwx").Rect(0, 0, 160, 90))
        self.assertIsNotNone(view.advance(0.04))
        canvas = Canvas(160, 90)
        view.paint(canvas)
        view.close()

    def test_sequential_stream(self):
        if not SAMPLE.exists():
            self.skipTest("Demo2.mp4 fehlt")
        stream = MediaStream(SAMPLE)
        try:
            first = stream.next_frame()
            self.assertIsNotNone(first)
            self.assertEqual((first.width, first.height), (3840, 2160))
        finally:
            stream.close()

    def test_audio_track(self):
        if not SAMPLE.exists():
            self.skipTest("Demo2.mp4 fehlt")
        audio = MediaAudio.from_file(SAMPLE, 1)
        self.assertGreater(audio.rate, 0)
        self.assertGreater(audio.channels, 0)
        self.assertGreater(len(audio.data), 0)

    def test_media_player(self):
        if not SAMPLE.exists():
            self.skipTest("Demo2.mp4 fehlt")
        player = MediaPlayer(SAMPLE, with_audio=False)
        try:
            player.play()
            frame = player.advance(0.04)
            self.assertIsNotNone(frame)
            self.assertGreater(player.time, 0)
        finally:
            player.close()

    def test_stream_seek(self):
        if not SAMPLE.exists():
            self.skipTest("Demo2.mp4 fehlt")
        stream = MediaStream(SAMPLE)
        try:
            stream.seek(1.0)
            frame = stream.next_frame()
            self.assertIsNotNone(frame)
        finally:
            stream.close()

    def test_audio_stream(self):
        if not SAMPLE.exists():
            self.skipTest("Demo2.mp4 fehlt")
        stream = MediaAudioStream(SAMPLE)
        try:
            self.assertEqual(stream.rate, 44100)
            chunk = stream.next_chunk()
            self.assertIsNotNone(chunk)
            self.assertGreater(len(chunk), 0)
        finally:
            stream.close()

    def test_audio_stream_seek(self):
        if not SAMPLE.exists():
            self.skipTest("Demo2.mp4 fehlt")
        stream = MediaAudioStream(SAMPLE)
        try:
            stream.seek(1.0)
            chunk = stream.next_chunk()
            self.assertIsNotNone(chunk)
        finally:
            stream.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
