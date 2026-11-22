"""Minimal AVI/MJPEG video reader for AMFWX."""

from __future__ import annotations

import struct
from pathlib import Path

from .canvas import Canvas
from .jpeg import decode_jpeg


class AviVideo:
    def __init__(self, data):
        self.data = data
        self.frames = []
        self.width = 0
        self.height = 0
        self.fps = 25.0
        self._parse()

    @classmethod
    def from_file(cls, path):
        return cls(Path(path).read_bytes())

    def _parse(self):
        if self.data[:4] != b"RIFF" or self.data[8:12] != b"AVI ":
            raise ValueError("kein AVI")
        self._walk(12, len(self.data))

    def _walk(self, start, end):
        position = start
        while position + 8 <= end:
            name = self.data[position:position + 4]
            size = struct.unpack_from("<I", self.data, position + 4)[0]
            body = position + 8
            if name == b"LIST":
                kind = self.data[body:body + 4]
                if kind == b"movi":
                    self._walk(body + 4, min(end, body + size))
                else:
                    self._walk(body + 4, min(end, body + size))
            elif name == b"avih":
                self._parse_avih(body)
            elif name in (b"00dc", b"00db") or (name[2:] in (b"dc", b"db")):
                self.frames.append(self.data[body:body + size])
            position += 8 + size + (size & 1)

    def _parse_avih(self, offset):
        values = struct.unpack_from("<IIIIIIII", self.data, offset)
        micro = values[0]
        self.fps = 1_000_000 / micro if micro else 25.0
        self.width, self.height = values[6], values[7]

    @property
    def duration(self):
        return len(self.frames) / self.fps if self.fps else 0.0

    def frame(self, index):
        width, height, pixels = decode_jpeg(self.frames[int(index)])
        canvas = Canvas(width, height)
        canvas.data[:] = pixels
        return canvas


class VideoPlayer:
    def __init__(self, video):
        self.video = video
        self.time = 0.0

    def frame_index(self):
        frames = getattr(self.video, "frames", 0)
        count = frames if isinstance(frames, int) else len(frames)
        return min(max(0, count - 1), int(self.time * self.video.fps))

    def frame(self):
        frames = getattr(self.video, "frames", 0)
        if not frames:
            return None
        return self.video.frame(self.frame_index())

    def advance(self, seconds):
        self.time = min(self.video.duration, self.time + seconds)
        return self.frame()
