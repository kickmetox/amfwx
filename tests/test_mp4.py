"""MP4 metadata parser tests."""

from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.mp4 import Mp4Info


def box(kind, payload):
    return struct.pack(">I", len(payload) + 8) + kind + payload


def make_mp4():
    ftyp = box(b"ftyp", b"isom" + b"\x00\x00\x02\x00" + b"isomiso2avc1")
    mvhd = box(b"mvhd", b"\x00\x00\x00\x00" + b"\x00" * 8 +
               struct.pack(">I", 1000) + struct.pack(">I", 5000) +
               b"\x00" * 80)
    tkhd_payload = bytearray(84)
    struct.pack_into(">I", tkhd_payload, 76, 320 * 65536)
    struct.pack_into(">I", tkhd_payload, 80, 240 * 65536)
    tkhd = box(b"tkhd", bytes(tkhd_payload))
    mdhd = box(b"mdhd", b"\x00\x00\x00\x00" + b"\x00" * 8 +
               struct.pack(">I", 1000) + struct.pack(">I", 5000) +
               b"\x00" * 80)
    hdlr = box(b"hdlr", b"\x00\x00\x00\x00" + b"\x00" * 4 + b"vide" +
               b"\x00" * 12)
    entry = bytearray(86)
    struct.pack_into(">I", entry, 0, 86)
    entry[4:8] = b"avc1"
    struct.pack_into(">H", entry, 32, 320)
    struct.pack_into(">H", entry, 34, 240)
    stsd = box(b"stsd", b"\x00\x00\x00\x00" + struct.pack(">I", 1) +
               bytes(entry))
    stbl = box(b"stbl", stsd)
    minf = box(b"minf", stbl)
    mdia = box(b"mdia", mdhd + hdlr + minf)
    trak = box(b"trak", tkhd + mdia)
    return box(b"moov", mvhd + trak) + ftyp


class Mp4Tests(unittest.TestCase):
    def test_metadata(self):
        info = Mp4Info(make_mp4())
        self.assertEqual(info.major_brand, "isom")
        self.assertEqual((info.timescale, info.duration), (1000, 5000))
        self.assertEqual(len(info.tracks), 1)
        track = info.tracks[0]
        self.assertEqual((track.kind, track.codec), ("vide", "avc1"))
        self.assertEqual((track.width, track.height), (320, 240))


if __name__ == "__main__":
    unittest.main(verbosity=2)
