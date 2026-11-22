"""Standard MIDI File parsing and basic winmm playback."""

from __future__ import annotations

import struct
import threading
import time


class MidiNote:
    def __init__(self, start, duration, pitch, velocity, channel):
        self.start = start
        self.duration = duration
        self.pitch = pitch
        self.velocity = velocity
        self.channel = channel

    def __repr__(self):
        return (f"MidiNote(start={self.start:.3f}, "
                f"duration={self.duration:.3f}, pitch={self.pitch})")


class MidiFile:
    def __init__(self, data):
        self.data = data
        self.format = 0
        self.division = 480
        self.tracks = []
        self.tempo = 500000
        self.notes = []
        self._parse()

    @classmethod
    def from_file(cls, path):
        with open(path, "rb") as handle:
            return cls(handle.read())

    def _parse(self):
        if self.data[:4] != b"MThd" or len(self.data) < 14:
            raise ValueError("keine MIDI-Datei")
        length = struct.unpack_from(">I", self.data, 4)[0]
        self.format, track_count, self.division = struct.unpack_from(
            ">HHH", self.data, 8)
        position = 8 + length
        for _ in range(track_count):
            if self.data[position:position + 4] != b"MTrk":
                break
            size = struct.unpack_from(">I", self.data, position + 4)[0]
            body = self.data[position + 8:position + 8 + size]
            self.tracks.append(body)
            position += 8 + size
        for track in self.tracks:
            self._parse_track(track)
        self.notes.sort(key=lambda note: note.start)

    def _parse_track(self, body):
        position = 0
        time_ticks = 0
        running = 0
        active = {}
        while position < len(body):
            delta, position = _variable(body, position)
            time_ticks += delta
            if position >= len(body):
                break
            status = body[position]
            if status & 0x80:
                position += 1
                if status < 0xF0:
                    running = status
            else:
                status = running
                if not status:
                    break
            if status == 0xFF:
                if position >= len(body):
                    break
                kind = body[position]
                position += 1
                length, position = _variable(body, position)
                payload = body[position:position + length]
                position += length
                if kind == 0x51 and len(payload) >= 3:
                    self.tempo = int.from_bytes(payload[:3], "big")
                continue
            if status in (0xF0, 0xF7):
                length, position = _variable(body, position)
                position += length
                continue
            command = status & 0xF0
            channel = status & 0x0F
            count = 1 if command in (0xC0, 0xD0) else 2
            if position + count > len(body):
                break
            first = body[position]
            second = body[position + 1] if count == 2 else 0
            position += count
            if command == 0x90 and second > 0:
                active[(channel, first)] = (time_ticks, second)
            elif command in (0x80, 0x90):
                key = (channel, first)
                if key in active:
                    start, velocity = active.pop(key)
                    self.notes.append(MidiNote(
                        self._seconds(start), self._seconds(time_ticks - start),
                        first, velocity, channel))
        for (channel, pitch), (start, velocity) in active.items():
            self.notes.append(MidiNote(
                self._seconds(start), 0.0, pitch, velocity, channel))

    def _seconds(self, ticks):
        tempo = self.tempo or 500000
        return ticks / float(self.division or 480) * (tempo / 1000000.0)

    @property
    def duration(self):
        return max((note.start + note.duration for note in self.notes),
                   default=0.0)


def _variable(data, position):
    value = 0
    while position < len(data):
        byte = data[position]
        position += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            break
    return value, position


class MidiPlayer:
    def __init__(self):
        import ctypes
        self.winmm = ctypes.WinDLL("winmm")
        self.device = ctypes.c_void_p()
        self.winmm.midiOutOpen.argtypes = [ctypes.POINTER(ctypes.c_void_p),
                                           ctypes.c_uint, ctypes.c_void_p,
                                           ctypes.c_void_p, ctypes.c_uint]
        self.winmm.midiOutShortMsg.argtypes = [ctypes.c_void_p,
                                               ctypes.c_uint]
        self.winmm.midiOutClose.argtypes = [ctypes.c_void_p]
        code = self.winmm.midiOutOpen(ctypes.byref(self.device),
                                      0xFFFFFFFF, None, None, 0)
        if code:
            raise OSError(f"midiOutOpen: {code}")
        self._stop = threading.Event()
        self._thread = None

    def play(self, midi):
        self.stop()
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, args=(midi,), daemon=True)
        self._thread.start()
        return self

    def _run(self, midi):
        start = time.monotonic()
        for note in midi.notes:
            wait = start + note.start - time.monotonic()
            if wait > 0 and self._stop.wait(wait):
                break
            if self._stop.is_set():
                break
            self.winmm.midiOutShortMsg(
                self.device, 0x90 | note.channel |
                (note.pitch << 8) | (note.velocity << 16))
            end = start + note.start + note.duration
            delay = end - time.monotonic()
            if delay > 0:
                self._stop.wait(delay)
            self.winmm.midiOutShortMsg(
                self.device, 0x80 | note.channel | (note.pitch << 8))

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        return self

    def close(self):
        self.stop()
        if self.device:
            self.winmm.midiOutClose(self.device)
            self.device = ctypes.c_void_p()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
