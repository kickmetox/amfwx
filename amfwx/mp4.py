"""Minimal ISO-BMFF/MP4 metadata parser."""

from __future__ import annotations

import struct
from pathlib import Path


class Mp4Error(ValueError):
    pass


class Mp4Track:
    def __init__(self):
        self.kind = ""
        self.codec = ""
        self.width = 0
        self.height = 0
        self.timescale = 0
        self.duration = 0

    def __repr__(self):
        return (f"Mp4Track(kind={self.kind!r}, codec={self.codec!r}, "
                f"size={self.width}x{self.height}, duration={self.duration})")


class Mp4Info:
    def __init__(self, data):
        self.data = data
        self.major_brand = ""
        self.timescale = 0
        self.duration = 0
        self.tracks = []
        self._parse()

    @classmethod
    def from_file(cls, path):
        return cls(Path(path).read_bytes())

    def _parse(self):
        if len(self.data) < 12:
            raise Mp4Error("zu kurz")
        for box_type, payload in _boxes(self.data, 0, len(self.data)):
            if box_type == b"ftyp":
                self.major_brand = payload[:4].decode("ascii", "replace")
            elif box_type == b"moov":
                self._parse_moov(payload)

    def _parse_moov(self, payload):
        for box_type, body in _boxes(payload, 0, len(payload)):
            if box_type == b"mvhd":
                self.timescale, self.duration = _mvhd(body)
            elif box_type == b"trak":
                track = self._parse_trak(body)
                if track is not None:
                    self.tracks.append(track)
        if self.timescale == 0 and self.tracks:
            self.timescale = self.tracks[0].timescale
            self.duration = self.tracks[0].duration

    def _parse_trak(self, payload):
        track = Mp4Track()
        for box_type, body in _boxes(payload, 0, len(payload)):
            if box_type == b"tkhd":
                track.width, track.height = _tkhd(body)
            elif box_type == b"mdia":
                for inner, mdia_body in _boxes(body, 0, len(body)):
                    if inner == b"mdhd":
                        track.timescale, track.duration = _mvhd(mdia_body)
                    elif inner == b"hdlr":
                        if len(mdia_body) >= 12:
                            track.kind = mdia_body[8:12].decode("ascii",
                                                              "replace")
                    elif inner == b"minf":
                        for block, minf_body in _boxes(mdia_body, 0,
                                                       len(mdia_body)):
                            if block == b"stbl":
                                for table, table_body in _boxes(
                                        minf_body, 0, len(minf_body)):
                                    if table == b"stsd":
                                        track.codec, width, height = _stsd(
                                            table_body)
                                        track.width = track.width or width
                                        track.height = track.height or height
        return track if track.kind else None


def _boxes(data, start, end):
    position = start
    while position + 8 <= end:
        size = struct.unpack_from(">I", data, position)[0]
        box_type = data[position + 4:position + 8]
        header = 8
        if size == 1:
            if position + 16 > end:
                break
            size = struct.unpack_from(">Q", data, position + 8)[0]
            header = 16
        elif size == 0:
            size = end - position
        if size < header or position + size > end:
            break
        yield box_type, data[position + header:position + size]
        position += size


def _mvhd(payload):
    if not payload:
        return 0, 0
    version = payload[0]
    if version == 1 and len(payload) >= 28:
        timescale = struct.unpack_from(">I", payload, 20)[0]
        duration = struct.unpack_from(">Q", payload, 24)[0]
    elif len(payload) >= 20:
        timescale = struct.unpack_from(">I", payload, 12)[0]
        duration = struct.unpack_from(">I", payload, 16)[0]
    else:
        return 0, 0
    return timescale, duration


def _tkhd(payload):
    if len(payload) < 84:
        return 0, 0
    width = struct.unpack_from(">I", payload, len(payload) - 8)[0] / 65536
    height = struct.unpack_from(">I", payload, len(payload) - 4)[0] / 65536
    return int(width), int(height)


def _stsd(payload):
    if len(payload) < 16:
        return "", 0, 0
    offset = 8
    size = struct.unpack_from(">I", payload, offset)[0]
    codec = payload[offset + 4:offset + 8].decode("ascii", "replace")
    if offset + size > len(payload):
        return codec, 0, 0
    # VisualSampleEntry: width/height at +32/+34 from entry start.
    entry = payload[offset:offset + size]
    if len(entry) >= 36:
        width = struct.unpack_from(">H", entry, 32)[0]
        height = struct.unpack_from(">H", entry, 34)[0]
        return codec, width, height
    return codec, 0, 0
