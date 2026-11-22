"""AVI/MJPEG video tests."""

from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.video import AviVideo
from tests.test_jpeg import JPEG


def make_avi():
    avih = struct.pack("<IIIIIIII", 40000, 0, 0, 0, 1, 0, 16, 16) + b"\x00" * 32
    strh = struct.pack("<4s4sIHHIIIIIIII", b"vids", b"MJPG", 0, 0, 0, 0, 1,
                       25, 0, 1, 0, 0xFFFFFFFF, 0)
    strf = struct.pack("<IiiHHIIiiII", 40, 16, 16, 1, 24, 0, 16 * 16 * 3,
                       0, 0, 0, 0)

    def chunk(name, data):
        return name + struct.pack("<I", len(data)) + data + (
            b"\x00" if len(data) % 2 else b"")

    hdrl = chunk(b"avih", avih) + chunk(b"strh", strh) + chunk(b"strf", strf)
    hdrl = b"LIST" + struct.pack("<I", len(hdrl) + 4) + b"hdrl" + hdrl
    movi = chunk(b"00dc", JPEG)
    movi = b"LIST" + struct.pack("<I", len(movi) + 4) + b"movi" + movi
    body = b"AVI " + hdrl + movi
    return b"RIFF" + struct.pack("<I", len(body)) + body


class VideoTests(unittest.TestCase):
    def test_avi_mjpeg(self):
        video = AviVideo(make_avi())
        self.assertEqual((video.width, video.height), (16, 16))
        self.assertEqual(len(video.frames), 1)
        self.assertAlmostEqual(video.fps, 25.0)
        frame = video.frame(0)
        self.assertEqual((frame.width, frame.height), (16, 16))


if __name__ == "__main__":
    unittest.main(verbosity=2)
