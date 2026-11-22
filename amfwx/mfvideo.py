"""H.264/MP4 video decoding through Media Foundation."""

from __future__ import annotations

import ctypes
import os
from ctypes import c_int, c_ubyte, c_void_p, POINTER, byref
from pathlib import Path

from .canvas import Canvas, Color


def _library():
    path = os.path.join(os.path.dirname(__file__), "bin", "mfdecode.dll")
    library = ctypes.WinDLL(path)
    library.mf_probe.argtypes = [ctypes.c_wchar_p, POINTER(c_int),
                                 POINTER(c_int), POINTER(c_int)]
    library.mf_probe.restype = c_int
    library.mf_decode_frame.argtypes = [ctypes.c_wchar_p, c_int, c_void_p,
                                        c_int, POINTER(c_int),
                                        POINTER(c_int), POINTER(c_int)]
    library.mf_decode_frame.restype = c_int
    library.mf_open.argtypes = [ctypes.c_wchar_p, POINTER(c_int),
                                POINTER(c_int)]
    library.mf_open.restype = c_int
    library.mf_next.argtypes = [c_int, c_void_p, c_int, POINTER(c_int),
                                POINTER(c_int), POINTER(c_int)]
    library.mf_next.restype = c_int
    library.mf_close.argtypes = [c_int]
    library.mf_seek.argtypes = [c_int, ctypes.c_double]
    library.mf_seek.restype = c_int
    library.mf_audio_decode.argtypes = [ctypes.c_wchar_p, c_int, c_void_p,
                                        c_int, POINTER(c_int),
                                        POINTER(c_int), POINTER(c_int)]
    library.mf_audio_decode.restype = c_int
    library.mf_audio_open.argtypes = [ctypes.c_wchar_p, POINTER(c_int),
                                      POINTER(c_int), POINTER(c_int)]
    library.mf_audio_open.restype = c_int
    library.mf_audio_next.argtypes = [c_int, c_void_p, c_int]
    library.mf_audio_next.restype = c_int
    library.mf_audio_close.argtypes = [c_int]
    library.mf_audio_seek.argtypes = [c_int, ctypes.c_double]
    library.mf_audio_seek.restype = c_int
    return library


def probe_media_foundation():
    try:
        _library()
        return True
    except OSError:
        return False


class MediaVideo:
    def __init__(self, path):
        self.path = str(path)
        self.width = 0
        self.height = 0
        self.frames = 1
        self.fps = 25.0

    @classmethod
    def from_file(cls, path):
        return cls(path)

    def info(self):
        library = _library()
        width = c_int()
        height = c_int()
        frames = c_int()
        code = library.mf_probe(self.path, byref(width), byref(height),
                                byref(frames))
        if code != 0:
            raise ValueError(f"Media Foundation Probe: {code}")
        self.width, self.height, self.frames = (width.value, height.value,
                                                frames.value)
        return self

    def stream(self):
        return MediaStream(self.path)

    def frame(self, index=0):
        library = _library()
        width = c_int()
        height = c_int()
        stride = c_int()
        if self.width and self.height:
            w, h = self.width, self.height
        else:
            # Decode one frame to learn dimensions.
            size = 4096 * 2160 * 3 // 2
            buffer = (c_ubyte * size)()
            copied = library.mf_decode_frame(self.path, 0, buffer, size,
                                             byref(width), byref(height),
                                             byref(stride))
            if copied <= 0:
                raise ValueError(f"Media Foundation Decode: {copied}")
            w, h = width.value, height.value
            self.width, self.height = w, h
        size = w * h * 3 // 2
        buffer = (c_ubyte * size)()
        copied = library.mf_decode_frame(self.path, int(index), buffer, size,
                                         byref(width), byref(height),
                                         byref(stride))
        if copied <= 0:
            raise ValueError(f"Media Foundation Decode: {copied}")
        return _nv12_to_canvas(bytes(buffer), w, h)


def _nv12_to_canvas(data, width, height):
    canvas = Canvas(width, height)
    pixels = bytearray(width * height * 4)
    for y in range(height):
        row = y * width
        uv_row = width * height + (y // 2) * width
        for x in range(width):
            luminance = data[row + x]
            uv = uv_row + (x // 2) * 2
            u = data[uv] - 128
            v = data[uv + 1] - 128
            c = max(0, luminance - 16)
            r = (298 * c + 409 * v + 128) >> 8
            g = (298 * c - 100 * u - 208 * v + 128) >> 8
            b = (298 * c + 516 * u + 128) >> 8
            offset = (y * width + x) * 4
            pixels[offset:offset + 4] = bytes((
                max(0, min(255, b)), max(0, min(255, g)),
                max(0, min(255, r)), 255))
    canvas.data[:] = pixels
    return canvas


class MediaStream:
    def __init__(self, path):
        library = _library()
        width = c_int()
        height = c_int()
        self.handle = library.mf_open(str(path), byref(width), byref(height))
        if self.handle < 0:
            raise ValueError(f"Media Foundation Open: {self.handle}")
        self.width = width.value
        self.height = height.value
        self.stride = 0

    def seek(self, seconds):
        code = _library().mf_seek(self.handle, float(seconds))
        if code != 0:
            raise ValueError(f"Media Foundation Seek: {code}")
        return self

    def next_frame(self):
        library = _library()
        size = self.width * self.height * 3 // 2
        buffer = (c_ubyte * size)()
        width = c_int()
        height = c_int()
        stride = c_int()
        copied = library.mf_next(self.handle, buffer, size, byref(width),
                                 byref(height), byref(stride))
        if copied <= 0:
            return None
        self.stride = stride.value
        return _nv12_to_canvas(bytes(buffer), self.width, self.height)

    def close(self):
        if self.handle >= 0:
            _library().mf_close(self.handle)
            self.handle = -1

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


class MediaAudio:
    def __init__(self, path):
        self.path = str(path)
        self.rate = 0
        self.channels = 0
        self.bits = 0
        self.data = b""

    @classmethod
    def from_file(cls, path, seconds=10):
        audio = cls(path)
        library = _library()
        size = 48000 * 2 * 2 * max(1, int(seconds))
        buffer = (c_ubyte * size)()
        rate = c_int()
        channels = c_int()
        bits = c_int()
        copied = library.mf_audio_decode(audio.path, int(seconds), buffer,
                                         size, byref(rate), byref(channels),
                                         byref(bits))
        if copied <= 0:
            raise ValueError(f"Media Foundation Audio: {copied}")
        audio.rate, audio.channels, audio.bits = rate.value, channels.value, bits.value
        audio.data = bytes(buffer[:copied])
        return audio

    def wav(self):
        from .audio import Wav
        return Wav(self.channels or 2, self.rate or 48000,
                   self.bits or 16, self.data)

    def play(self):
        from .audio import AudioPlayer
        player = AudioPlayer()
        player.play(self.wav())
        return player


class MediaAudioStream:
    def __init__(self, path):
        library = _library()
        rate = c_int()
        channels = c_int()
        bits = c_int()
        self.handle = library.mf_audio_open(str(path), byref(rate),
                                            byref(channels), byref(bits))
        if self.handle < 0:
            raise ValueError(f"Media Foundation Audio Open: {self.handle}")
        self.rate = rate.value
        self.channels = channels.value
        self.bits = bits.value

    def seek(self, seconds):
        code = _library().mf_audio_seek(self.handle, float(seconds))
        if code != 0:
            raise ValueError(f"Media Foundation Audio Seek: {code}")
        return self

    def next_chunk(self, size=16384):
        library = _library()
        buffer = (c_ubyte * size)()
        copied = library.mf_audio_next(self.handle, buffer, size)
        if copied <= 0:
            return None
        return bytes(buffer[:copied])

    def play(self):
        from .audio import AudioQueuePlayer
        player = AudioQueuePlayer(self.channels, self.rate, self.bits)
        try:
            while True:
                chunk = self.next_chunk()
                if chunk is None:
                    break
                player.feed(chunk)
            player.wait()
        finally:
            player.stop()
        return self

    def close(self):
        if self.handle >= 0:
            _library().mf_audio_close(self.handle)
            self.handle = -1

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
