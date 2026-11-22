"""Pure-Python baseline JPEG decoder for AMFWX (no external codecs)."""

from __future__ import annotations

import math
import struct

ZIGZAG = [
    0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
    12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63,
]

_COS = [[(math.sqrt(0.5) if u == 0 else 1.0) *
         math.cos((2 * x + 1) * u * math.pi / 16) / 2
         for u in range(8)] for x in range(8)]
_SQRT2 = math.sqrt(2.0)


class JPEGError(ValueError):
    pass


class BitReader:
    def __init__(self, data, position):
        self.data = data
        self.position = position
        self.bits = 0
        self.count = 0

    def _byte(self):
        if self.position >= len(self.data):
            raise EOFError
        value = self.data[self.position]
        self.position += 1
        if value == 0xFF:
            while self.position < len(self.data) and self.data[self.position] == 0xFF:
                self.position += 1
            if self.position >= len(self.data):
                raise EOFError
            marker = self.data[self.position]
            self.position += 1
            if marker == 0:
                return 0xFF
            raise JPEGError(f"Marker 0xFF{marker:02X} im Entropiestrom")
        return value

    def bit(self):
        if self.count == 0:
            self.bits = self._byte()
            self.count = 8
        self.count -= 1
        return (self.bits >> self.count) & 1

    def read(self, count):
        value = 0
        for _ in range(count):
            value = (value << 1) | self.bit()
        return value

    def align(self):
        self.count = 0


def _huffman_table(counts, symbols):
    table = {}
    code = 0
    index = 0
    for length in range(1, 17):
        for _ in range(counts[length - 1]):
            table[(length, code)] = symbols[index]
            index += 1
            code += 1
        code <<= 1
    return table


def _decode_huffman(reader, table):
    code = 0
    for length in range(1, 17):
        code = (code << 1) | reader.bit()
        symbol = table.get((length, code))
        if symbol is not None:
            return symbol
    raise JPEGError("ungültiger Huffman-Code")


def _extend(value, bits):
    if bits and value < (1 << (bits - 1)):
        value -= (1 << bits) - 1
    return value


def _idct(coefficients, quantization):
    block = [[0.0] * 8 for _ in range(8)]
    for v in range(8):
        for u in range(8):
            index = ZIGZAG[v * 8 + u]
            block[v][u] = coefficients[index] * quantization[index]
    temp = [[0.0] * 8 for _ in range(8)]
    for y in range(8):
        for u in range(8):
            total = 0.0
            for v in range(8):
                total += _COS[y][v] * block[v][u]
            temp[y][u] = total
    output = [[0] * 8 for _ in range(8)]
    for y in range(8):
        for x in range(8):
            total = 0.0
            for u in range(8):
                total += _COS[x][u] * temp[y][u]
            output[y][x] = max(0, min(255, int(round(total + 128))))
    return output


def decode_jpeg(data):
    if data[:2] != b"\xff\xd8":
        raise JPEGError("kein JPEG")
    position = 2
    quantization = {}
    huffman_dc = {}
    huffman_ac = {}
    width = height = 0
    components = []
    restart_interval = 0
    while position < len(data):
        if data[position] != 0xFF:
            position += 1
            continue
        while position < len(data) and data[position] == 0xFF:
            position += 1
        if position >= len(data):
            break
        marker = data[position]
        position += 1
        if marker in (0xD8, 0xD9):
            continue
        length = struct.unpack_from(">H", data, position)[0]
        payload = data[position + 2:position + length]
        if marker == 0xDB:
            offset = 0
            while offset < len(payload):
                info = payload[offset]
                precision = info >> 4
                identifier = info & 0x0F
                offset += 1
                table = [0] * 64
                for index in range(64):
                    if precision:
                        table[index] = struct.unpack_from(">H", payload, offset)[0]
                        offset += 2
                    else:
                        table[index] = payload[offset]
                        offset += 1
                quantization[identifier] = table
        elif marker == 0xC0:
            precision, height, width, count = struct.unpack_from(">BHHB", payload, 0)
            if precision != 8:
                raise JPEGError("nur 8-bit JPEG")
            offset = 6
            for _ in range(count):
                identifier, sampling, table = struct.unpack_from(">BBB", payload, offset)
                offset += 3
                components.append({"id": identifier,
                                   "h": sampling >> 4,
                                   "v": sampling & 0x0F,
                                   "quant": table})
        elif marker == 0xC4:
            offset = 0
            while offset < len(payload):
                info = payload[offset]
                offset += 1
                counts = list(payload[offset:offset + 16])
                offset += 16
                total = sum(counts)
                symbols = list(payload[offset:offset + total])
                offset += total
                table = _huffman_table(counts, symbols)
                if info >> 4 == 0:
                    huffman_dc[info & 0x0F] = table
                else:
                    huffman_ac[info & 0x0F] = table
        elif marker == 0xDD:
            restart_interval = struct.unpack_from(">H", payload, 0)[0]
        elif marker == 0xDA:
            count = payload[0]
            scan = []
            offset = 1
            for _ in range(count):
                identifier, tables = payload[offset], payload[offset + 1]
                offset += 2
                scan.append((identifier, tables >> 4, tables & 0x0F))
            entropy = position + length
            return _decode_scan(data, entropy, width, height, components,
                                quantization, huffman_dc, huffman_ac, scan,
                                restart_interval)
        position += length
    raise JPEGError("kein SOS")


def _decode_scan(data, position, width, height, components, quantization,
                 huffman_dc, huffman_ac, scan, restart_interval):
    reader = BitReader(data, position)
    max_h = max(component["h"] for component in components)
    max_v = max(component["v"] for component in components)
    mcu_w = max_h * 8
    mcu_h = max_v * 8
    mcu_cols = (width + mcu_w - 1) // mcu_w
    mcu_rows = (height + mcu_h - 1) // mcu_h
    planes = {}
    for component in components:
        pw = mcu_cols * component["h"] * 8
        ph = mcu_rows * component["v"] * 8
        planes[component["id"]] = [[0] * pw for _ in range(ph)]
    predictors = {component["id"]: 0 for component in components}
    for my in range(mcu_rows):
        for mx in range(mcu_cols):
            for component in components:
                dc_table = huffman_dc[scan[0][1]]
                ac_table = huffman_ac[scan[0][2]]
                for entry in scan:
                    if entry[0] == component["id"]:
                        dc_table = huffman_dc[entry[1]]
                        ac_table = huffman_ac[entry[2]]
                        break
                for by in range(component["v"]):
                    for bx in range(component["h"]):
                        coefficients = [0] * 64
                        size = _decode_huffman(reader, dc_table)
                        difference = _extend(reader.read(size), size) if size else 0
                        predictors[component["id"]] += difference
                        coefficients[0] = predictors[component["id"]]
                        index = 1
                        while index < 64:
                            symbol = _decode_huffman(reader, ac_table)
                            if symbol == 0:
                                break
                            run, size = symbol >> 4, symbol & 0x0F
                            index += run
                            if index >= 64:
                                break
                            coefficients[index] = _extend(reader.read(size), size) if size else 0
                            index += 1
                        block = _idct(coefficients,
                                      quantization[component["quant"]])
                        plane = planes[component["id"]]
                        origin_x = (mx * component["h"] + bx) * 8
                        origin_y = (my * component["v"] + by) * 8
                        for y in range(8):
                            row = plane[origin_y + y]
                            for x in range(8):
                                row[origin_x + x] = block[y][x]
    # Upsample and convert.
    output = bytearray(width * height * 4)
    y_plane = planes[components[0]["id"]]
    for y in range(height):
        for x in range(width):
            component_values = []
            for component in components:
                plane = planes[component["id"]]
                sx = x * component["h"] // max_h
                sy = y * component["v"] // max_v
                component_values.append(plane[sy][sx])
            if len(component_values) >= 3:
                yy, cb, cr = component_values[:3]
                r = int(yy + 1.402 * (cr - 128))
                g = int(yy - 0.344136 * (cb - 128) - 0.714136 * (cr - 128))
                b = int(yy + 1.772 * (cb - 128))
            else:
                r = g = b = component_values[0]
            offset = (y * width + x) * 4
            output[offset:offset + 4] = bytes((max(0, min(255, b)),
                                               max(0, min(255, g)),
                                               max(0, min(255, r)), 255))
    return width, height, bytes(output)
