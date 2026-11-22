"""Pure-Python PNG codec for AMFWX (8-bit, non-interlaced)."""

from __future__ import annotations

import struct
import zlib


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def decode_png(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("kein PNG")
    position = 8
    width = height = 0
    bit_depth = color_type = 0
    palette = None
    compressed = bytearray()
    while position < len(data):
        length = struct.unpack_from(">I", data, position)[0]
        kind = data[position + 4:position + 8]
        payload = data[position + 8:position + 8 + length]
        position += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = \
                struct.unpack(">IIBBBBB", payload)
            if interlace:
                raise ValueError("interlaced PNG nicht unterstützt")
        elif kind == b"PLTE":
            palette = [tuple(payload[index:index + 3])
                       for index in range(0, len(payload), 3)]
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    if bit_depth != 8:
        raise ValueError("nur 8-bit PNG")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    if channels is None:
        raise ValueError("PNG-Farbtyp nicht unterstützt")
    raw = zlib.decompress(bytes(compressed))
    stride = width * channels
    rows = []
    previous = bytearray(stride)
    position = 0
    for _y in range(height):
        filter_type = raw[position]
        position += 1
        row = bytearray(raw[position:position + stride])
        position += stride
        for index in range(stride):
            left = row[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                row[index] = (row[index] + left) & 0xFF
            elif filter_type == 2:
                row[index] = (row[index] + up) & 0xFF
            elif filter_type == 3:
                row[index] = (row[index] + (left + up) // 2) & 0xFF
            elif filter_type == 4:
                row[index] = (row[index] + _paeth(left, up, upper_left)) & 0xFF
        rows.append(row)
        previous = row
    pixels = bytearray(width * height * 4)
    for y, row in enumerate(rows):
        for x in range(width):
            base = x * channels
            if color_type == 0:
                r = g = b = row[base]
                a = 255
            elif color_type == 2:
                r, g, b = row[base:base + 3]
                a = 255
            elif color_type == 3:
                index = row[base]
                r, g, b = palette[index] if palette else (0, 0, 0)
                a = 255
            elif color_type == 4:
                r = g = b = row[base]
                a = row[base + 1]
            else:
                r, g, b, a = row[base:base + 4]
            offset = (y * width + x) * 4
            pixels[offset:offset + 4] = bytes((b, g, r, a))
    return width, height, bytes(pixels)


def encode_png(width, height, bgra):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        row = bytearray()
        for x in range(width):
            offset = (y * width + x) * 4
            b, g, r, a = bgra[offset:offset + 4]
            row.extend((r, g, b, a))
        raw.extend(row)

    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + \
            struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))
