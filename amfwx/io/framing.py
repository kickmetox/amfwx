"""Framing helpers for serial, USB and TCP links."""

from __future__ import annotations

import struct


class FrameError(ValueError):
    pass


def encode_length_prefixed(payload):
    data = bytes(payload)
    return struct.pack("<I", len(data)) + data


def cobs_encode(data):
    data = bytes(data)
    output = bytearray([0])
    code_index = 0
    code = 1
    for byte in data:
        if byte == 0:
            output[code_index] = code
            code_index = len(output)
            output.append(0)
            code = 1
        else:
            output.append(byte)
            code += 1
            if code == 0xFF:
                output[code_index] = code
                code_index = len(output)
                output.append(0)
                code = 1
    output[code_index] = code
    return bytes(output)


def cobs_decode(data):
    data = bytes(data)
    output = bytearray()
    index = 0
    while index < len(data):
        code = data[index]
        index += 1
        if code == 0:
            raise FrameError("COBS: ungueltiger Block")
        for _ in range(code - 1):
            if index >= len(data):
                raise FrameError("COBS: abgeschnitten")
            output.append(data[index])
            index += 1
        if code < 0xFF and index < len(data):
            output.append(0)
    return bytes(output)


class FrameDecoder:
    def __init__(self, delimiter=b"\n", maximum=1024 * 1024):
        self.delimiter = bytes(delimiter)
        self.maximum = int(maximum)
        self.buffer = bytearray()

    def feed(self, data):
        self.buffer.extend(data)
        if len(self.buffer) > self.maximum:
            raise FrameError("Frame zu gross")
        frames = []
        while True:
            index = self.buffer.find(self.delimiter)
            if index < 0:
                break
            frame = bytes(self.buffer[:index])
            del self.buffer[:index + len(self.delimiter)]
            if frame:
                frames.append(frame)
        return frames

    def reset(self):
        self.buffer.clear()
        return self


class LengthDecoder:
    def __init__(self, maximum=1024 * 1024):
        self.maximum = int(maximum)
        self.buffer = bytearray()

    def feed(self, data):
        self.buffer.extend(data)
        frames = []
        while len(self.buffer) >= 4:
            length = struct.unpack("<I", self.buffer[:4])[0]
            if length > self.maximum:
                raise FrameError("Laenge zu gross")
            if len(self.buffer) < 4 + length:
                break
            frames.append(bytes(self.buffer[4:4 + length]))
            del self.buffer[:4 + length]
        return frames
