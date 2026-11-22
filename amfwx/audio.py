"""Minimal WAV playback via Windows waveOut."""

from __future__ import annotations

import ctypes
import struct
from ctypes import POINTER, byref, c_char_p, c_int, c_uint, c_void_p, wintypes

winmm = ctypes.WinDLL("winmm")
WAVE_MAPPER = 0xFFFFFFFF


class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [
        ("wFormatTag", ctypes.c_ushort),
        ("nChannels", ctypes.c_ushort),
        ("nSamplesPerSec", ctypes.c_uint),
        ("nAvgBytesPerSec", ctypes.c_uint),
        ("nBlockAlign", ctypes.c_ushort),
        ("wBitsPerSample", ctypes.c_ushort),
        ("cbSize", ctypes.c_ushort),
    ]


class WAVEHDR(ctypes.Structure):
    _fields_ = [
        ("lpData", c_void_p),
        ("dwBufferLength", c_uint),
        ("dwBytesRecorded", c_uint),
        ("dwUser", ctypes.c_size_t),
        ("dwFlags", c_uint),
        ("dwLoops", c_uint),
        ("lpNext", c_void_p),
        ("reserved", ctypes.c_size_t),
    ]


winmm.waveOutOpen.argtypes = [POINTER(c_void_p), c_uint,
                              POINTER(WAVEFORMATEX), c_void_p, c_void_p,
                              c_uint]
winmm.waveOutOpen.restype = c_uint
winmm.waveOutPrepareHeader.argtypes = [c_void_p, POINTER(WAVEHDR), c_uint]
winmm.waveOutWrite.argtypes = [c_void_p, POINTER(WAVEHDR), c_uint]
winmm.waveOutUnprepareHeader.argtypes = [c_void_p, POINTER(WAVEHDR), c_uint]
winmm.waveOutReset.argtypes = [c_void_p]
winmm.waveOutClose.argtypes = [c_void_p]
winmm.waveOutGetPosition.argtypes = [c_void_p, c_void_p, c_uint]
WHDR_DONE = 0x00000001


class Wav:
    def __init__(self, channels, rate, bits, data):
        self.channels = channels
        self.rate = rate
        self.bits = bits
        self.data = data

    @property
    def duration(self):
        return len(self.data) / max(1, self.channels * self.rate *
                                    (self.bits // 8))


def decode_wav(data):
    if data[:4] not in (b"RIFF", b"RF64") or data[8:12] != b"WAVE":
        raise ValueError("kein WAV")
    position = 12
    fmt = None
    payload = None
    while position + 8 <= len(data):
        name = data[position:position + 4]
        size = struct.unpack_from("<I", data, position + 4)[0]
        body = data[position + 8:position + 8 + size]
        if name == b"fmt ":
            fmt = body
        elif name == b"data":
            payload = body
        position += 8 + size + (size & 1)
    if fmt is None or payload is None:
        raise ValueError("WAV ohne fmt/data")
    tag, channels, rate, _avg, _align, bits = struct.unpack_from(
        "<HHIIHH", fmt, 0)
    if tag not in (1, 3):
        raise ValueError("nur PCM/IEEE-Float-WAV")
    return Wav(channels, rate, bits, payload)


class AudioPlayer:
    def __init__(self):
        self.device = c_void_p()
        self.header = None
        self.buffer = None

    def play_wav(self, path):
        data = decode_wav(open(path, "rb").read())
        return self.play(data)

    def play(self, wav):
        self.stop()
        fmt = WAVEFORMATEX()
        fmt.wFormatTag = 1
        fmt.nChannels = wav.channels
        fmt.nSamplesPerSec = wav.rate
        fmt.wBitsPerSample = wav.bits
        fmt.nBlockAlign = wav.channels * (wav.bits // 8)
        fmt.nAvgBytesPerSec = wav.rate * fmt.nBlockAlign
        code = winmm.waveOutOpen(byref(self.device), WAVE_MAPPER, byref(fmt),
                                 None, None, 0)
        if code:
            raise OSError(f"waveOutOpen: {code}")
        self.buffer = ctypes.create_string_buffer(wav.data, len(wav.data))
        self.header = WAVEHDR()
        self.header.lpData = ctypes.cast(self.buffer, c_void_p)
        self.header.dwBufferLength = len(wav.data)
        winmm.waveOutPrepareHeader(self.device, byref(self.header),
                                   ctypes.sizeof(WAVEHDR))
        winmm.waveOutWrite(self.device, byref(self.header),
                           ctypes.sizeof(WAVEHDR))
        return self

    def position(self):
        if not self.device:
            return 0.0
        time = (ctypes.c_ubyte * 16)()
        ctypes.memset(time, 0, 16)
        ctypes.cast(time, POINTER(ctypes.c_uint))[0] = 1  # TIME_MS
        if winmm.waveOutGetPosition(self.device, time, 16):
            return 0.0
        milliseconds = ctypes.cast(time, POINTER(ctypes.c_uint))[1]
        return milliseconds / 1000.0

    def stop(self):
        if self.device:
            winmm.waveOutReset(self.device)
            if self.header is not None:
                winmm.waveOutUnprepareHeader(self.device, byref(self.header),
                                             ctypes.sizeof(WAVEHDR))
            winmm.waveOutClose(self.device)
        self.device = c_void_p()
        self.header = None
        self.buffer = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.stop()


class AudioQueuePlayer:
    """Queue PCM chunks to waveOut without building one large WAV."""

    def __init__(self, channels=2, rate=48000, bits=16):
        self.device = c_void_p()
        self.channels = channels
        self.rate = rate
        self.bits = bits
        self.entries = []
        fmt = WAVEFORMATEX()
        fmt.wFormatTag = 1
        fmt.nChannels = channels
        fmt.nSamplesPerSec = rate
        fmt.wBitsPerSample = bits
        fmt.nBlockAlign = channels * (bits // 8)
        fmt.nAvgBytesPerSec = rate * fmt.nBlockAlign
        code = winmm.waveOutOpen(byref(self.device), WAVE_MAPPER, byref(fmt),
                                 None, None, 0)
        if code:
            raise OSError(f"waveOutOpen: {code}")

    def feed(self, data):
        if not self.device:
            raise OSError("waveOut nicht offen")
        self._clean()
        buffer = ctypes.create_string_buffer(bytes(data), len(data))
        header = WAVEHDR()
        header.lpData = ctypes.cast(buffer, c_void_p)
        header.dwBufferLength = len(data)
        winmm.waveOutPrepareHeader(self.device, byref(header),
                                   ctypes.sizeof(WAVEHDR))
        winmm.waveOutWrite(self.device, byref(header),
                           ctypes.sizeof(WAVEHDR))
        self.entries.append((header, buffer))
        return self

    def _clean(self):
        self.entries = [(header, buffer) for header, buffer in self.entries
                        if not (header.dwFlags & WHDR_DONE)]

    def wait(self):
        import time
        while True:
            self._clean()
            if not self.entries:
                break
            time.sleep(0.01)
        return self

    def stop(self):
        if self.device:
            winmm.waveOutReset(self.device)
            for header, _buffer in self.entries:
                winmm.waveOutUnprepareHeader(self.device, byref(header),
                                             ctypes.sizeof(WAVEHDR))
            winmm.waveOutClose(self.device)
        self.device = c_void_p()
        self.entries = []

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.stop()
