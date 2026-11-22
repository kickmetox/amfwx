"""Minimal TrueType parser and rasterizer for AMFWX.

Supports simple glyphs, cmap format 4, loca/hmtx and quadratic outlines.
No GSUB/GPOS shaping, no composite glyphs, no hinting.
"""

from __future__ import annotations

import struct
from pathlib import Path

from .canvas import Color, Rect


def _u16(data, offset):
    return struct.unpack_from(">H", data, offset)[0]


def _s16(data, offset):
    return struct.unpack_from(">h", data, offset)[0]


def _u32(data, offset):
    return struct.unpack_from(">I", data, offset)[0]


class TrueTypeFont:
    def __init__(self, path, size=16):
        self.path = str(path)
        self.data = Path(path).read_bytes()
        self.size = float(size)
        self._parse_tables()
        self._parse_cmap()
        self._parse_kern()
        self._parse_gsub()
        self._parse_gpos()
        self._glyph_cache = {}
        self._outline_cache = {}

    def _parse_tables(self):
        data = self.data
        if len(data) < 12:
            raise ValueError("kein TTF")
        count = _u16(data, 4)
        self.tables = {}
        for index in range(count):
            offset = 12 + index * 16
            tag = data[offset:offset + 4].decode("latin1")
            table_offset = _u32(data, offset + 8)
            length = _u32(data, offset + 12)
            self.tables[tag] = (table_offset, length)
        head = self.tables.get("head")
        maxp = self.tables.get("maxp")
        hhea = self.tables.get("hhea")
        if not all((head, maxp, hhea)):
            raise ValueError("TTF-Tabellen fehlen")
        self.units_per_em = _u16(data, head[0] + 18)
        self.index_to_loc = _s16(data, head[0] + 50)
        self.num_glyphs = _u16(data, maxp[0] + 4)
        self.ascent = _s16(data, hhea[0] + 4)
        self.descent = _s16(data, hhea[0] + 6)
        self.num_hmetrics = _u16(data, hhea[0] + 34)
        self.scale = self.size / max(1, self.units_per_em)
        self._loca = self._read_loca()
        self._hmtx_offset = self.tables["hmtx"][0]

    def _read_loca(self):
        offset, length = self.tables["loca"]
        count = self.num_glyphs + 1
        values = []
        if self.index_to_loc == 0:
            for index in range(count):
                values.append(_u16(self.data, offset + index * 2) * 2)
        else:
            for index in range(count):
                values.append(_u32(self.data, offset + index * 4))
        return values

    def _parse_cmap(self):
        offset, _length = self.tables["cmap"]
        count = _u16(self.data, offset + 2)
        best = None
        for index in range(count):
            record = offset + 4 + index * 8
            platform = _u16(self.data, record)
            encoding = _u16(self.data, record + 2)
            sub = offset + _u32(self.data, record + 4)
            fmt = _u16(self.data, sub)
            if fmt == 4 and (platform, encoding) in ((3, 1), (0, 3), (3, 10)):
                best = sub
        if best is None:
            for index in range(count):
                record = offset + 4 + index * 8
                sub = offset + _u32(self.data, record + 4)
                if _u16(self.data, sub) == 4:
                    best = sub
                    break
        self.cmap = {}
        if best is None:
            return
        sub = best
        seg_count = _u16(self.data, sub + 6) // 2
        end_offset = sub + 14
        start_offset = end_offset + seg_count * 2 + 2
        delta_offset = start_offset + seg_count * 2
        range_offset = delta_offset + seg_count * 2
        for segment in range(seg_count):
            end = _u16(self.data, end_offset + segment * 2)
            start = _u16(self.data, start_offset + segment * 2)
            delta = _s16(self.data, delta_offset + segment * 2)
            range_value = _u16(self.data, range_offset + segment * 2)
            if start == 0xFFFF:
                continue
            for code in range(start, min(end, 0xFFFE) + 1):
                if range_value == 0:
                    glyph = (code + delta) & 0xFFFF
                else:
                    address = range_offset + segment * 2 + range_value + \
                        (code - start) * 2
                    if address + 2 > len(self.data):
                        continue
                    glyph = _u16(self.data, address)
                    if glyph:
                        glyph = (glyph + delta) & 0xFFFF
                if glyph:
                    self.cmap[code] = glyph

    def _parse_kern(self):
        self.kern = {}
        if "kern" not in self.tables:
            return
        offset, _length = self.tables["kern"]
        try:
            version = _u16(self.data, offset)
            count = _u16(self.data, offset + 2)
            position = offset + 4
            for _index in range(count):
                length = _u16(self.data, position + 2)
                coverage = _u16(self.data, position + 4)
                if (coverage >> 8) == 0:
                    pairs = _u16(self.data, position + 6)
                    pair_offset = position + 14
                    for pair in range(pairs):
                        left = _u16(self.data, pair_offset + pair * 6)
                        right = _u16(self.data, pair_offset + pair * 6 + 2)
                        value = _s16(self.data, pair_offset + pair * 6 + 4)
                        self.kern[(left, right)] = value
                position += length
        except Exception:
            self.kern = {}

    def _parse_gsub(self):
        self.ligatures = {}
        if "GSUB" not in self.tables:
            return
        base = self.tables["GSUB"][0]
        try:
            lookup_list = base + _u16(self.data, base + 8)
            count = _u16(self.data, lookup_list)
            for index in range(count):
                lookup = lookup_list + _u16(self.data, lookup_list + 2 + index * 2)
                lookup_type = _u16(self.data, lookup)
                sub_count = _u16(self.data, lookup + 4)
                if lookup_type not in (4, 7):
                    continue
                for sub_index in range(sub_count):
                    sub = lookup + _u16(self.data, lookup + 6 + sub_index * 2)
                    if lookup_type == 7 and _u16(self.data, sub) == 1:
                        extension_type = _u16(self.data, sub + 2)
                        offset = _u32(self.data, sub + 4)
                        if extension_type == 4:
                            self._parse_ligature_subtable(sub + offset)
                    else:
                        self._parse_ligature_subtable(sub)
        except Exception:
            self.ligatures = {}

    def _coverage(self, offset):
        glyphs = set()
        fmt = _u16(self.data, offset)
        if fmt == 1:
            count = _u16(self.data, offset + 2)
            for index in range(count):
                glyphs.add(_u16(self.data, offset + 4 + index * 2))
        elif fmt == 2:
            count = _u16(self.data, offset + 2)
            for index in range(count):
                start = _u16(self.data, offset + 4 + index * 6)
                end = _u16(self.data, offset + 6 + index * 6)
                glyphs.update(range(start, end + 1))
        return glyphs

    def _parse_ligature_subtable(self, sub):
        if _u16(self.data, sub) != 1:
            return
        coverage = self._coverage(sub + _u16(self.data, sub + 2))
        set_count = _u16(self.data, sub + 4)
        for index in range(set_count):
            set_offset = sub + _u16(self.data, sub + 6 + index * 2)
            lig_count = _u16(self.data, set_offset)
            for lig_index in range(lig_count):
                ligature = set_offset + _u16(self.data,
                                             set_offset + 2 + lig_index * 2)
                lig_glyph = _u16(self.data, ligature)
                components = _u16(self.data, ligature + 2)
                if components < 2:
                    continue
                glyphs = tuple(_u16(self.data, ligature + 4 + part * 2)
                               for part in range(components - 1))
                if glyphs:
                    self.ligatures.setdefault(glyphs[0], []).append(
                        (glyphs, lig_glyph))

    def shape(self, text):
        glyphs = [self.glyph_id(character) for character in str(text)]
        index = 0
        while index < len(glyphs):
            candidates = self.ligatures.get(glyphs[index], [])
            replaced = False
            for components, ligature in candidates:
                if len(components) < 2:
                    continue
                if tuple(glyphs[index:index + len(components)]) == components:
                    glyphs[index:index + len(components)] = [ligature]
                    replaced = True
                    break
            if not replaced:
                index += 1
        return glyphs

    def _parse_gpos(self):
        self.gpos_pairs = {}
        self.gpos_class_tables = []
        self.mark_positions = {}
        self.mark_mark_positions = {}
        self.mark_ligature_positions = {}
        self.mark_glyphs = set()
        self.base_glyphs = set()
        if "GPOS" not in self.tables:
            return
        base = self.tables["GPOS"][0]
        try:
            lookup_list = base + _u16(self.data, base + 8)
            count = _u16(self.data, lookup_list)
            for index in range(count):
                lookup = lookup_list + _u16(self.data, lookup_list + 2 + index * 2)
                lookup_type = _u16(self.data, lookup)
                sub_count = _u16(self.data, lookup + 4)
                if lookup_type not in (2, 4, 5, 6, 9):
                    continue
                for sub_index in range(sub_count):
                    sub = lookup + _u16(self.data, lookup + 6 + sub_index * 2)
                    if lookup_type == 9 and _u16(self.data, sub) == 1:
                        extension_type = _u16(self.data, sub + 2)
                        offset = _u32(self.data, sub + 4)
                        if extension_type == 2:
                            self._parse_pair_subtable(sub + offset)
                        elif extension_type == 4:
                            self._parse_mark_base_subtable(sub + offset)
                        elif extension_type == 6:
                            self._parse_mark_mark_subtable(sub + offset)
                        elif extension_type == 5:
                            self._parse_mark_ligature_subtable(sub + offset)
                    elif lookup_type == 2:
                        self._parse_pair_subtable(sub)
                    elif lookup_type == 4:
                        self._parse_mark_base_subtable(sub)
                    elif lookup_type == 6:
                        self._parse_mark_mark_subtable(sub)
                    elif lookup_type == 5:
                        self._parse_mark_ligature_subtable(sub)
        except Exception:
            self.gpos_pairs = {}

    def _anchor(self, offset):
        fmt = _u16(self.data, offset)
        if fmt in (1, 2, 3):
            return _s16(self.data, offset + 2), _s16(self.data, offset + 4)
        return 0, 0

    def _parse_mark_mark_subtable(self, sub):
        if _u16(self.data, sub) != 1:
            return
        mark1_coverage = self._coverage(sub + _u16(self.data, sub + 2))
        mark2_coverage = self._coverage(sub + _u16(self.data, sub + 4))
        class_count = _u16(self.data, sub + 6)
        mark1_array = sub + _u16(self.data, sub + 8)
        mark2_array = sub + _u16(self.data, sub + 10)
        count1 = _u16(self.data, mark1_array)
        marks1 = []
        for index in range(count1):
            record = mark1_array + 2 + index * 4
            mark_class = _u16(self.data, record)
            anchor = self._anchor(mark1_array + _u16(self.data, record + 2))
            marks1.append((mark_class, anchor))
        count2 = _u16(self.data, mark2_array)
        marks2 = []
        for index in range(count2):
            record = mark2_array + 2 + index * class_count * 2
            anchors = []
            for class_index in range(class_count):
                offset = _u16(self.data, record + class_index * 2)
                anchors.append(self._anchor(mark2_array + offset) if offset else (0, 0))
            marks2.append(anchors)
        mark1_list = sorted(mark1_coverage)
        mark2_list = sorted(mark2_coverage)
        for index1, mark1 in enumerate(mark1_list):
            if index1 >= len(marks1):
                break
            mark_class, (x1, y1) = marks1[index1]
            if mark_class >= class_count:
                continue
            self.mark_glyphs.add(mark1)
            for index2, mark2 in enumerate(mark2_list):
                if index2 >= len(marks2):
                    break
                x2, y2 = marks2[index2][mark_class]
                self.mark_mark_positions[(mark2, mark1)] = (x2 - x1, y2 - y1)

    def _parse_mark_ligature_subtable(self, sub):
        if _u16(self.data, sub) != 1:
            return
        mark_coverage = self._coverage(sub + _u16(self.data, sub + 2))
        ligature_coverage = self._coverage(sub + _u16(self.data, sub + 4))
        class_count = _u16(self.data, sub + 6)
        mark_array = sub + _u16(self.data, sub + 8)
        ligature_array = sub + _u16(self.data, sub + 10)
        mark_count = _u16(self.data, mark_array)
        marks = []
        for index in range(mark_count):
            record = mark_array + 2 + index * 4
            mark_class = _u16(self.data, record)
            anchor = self._anchor(mark_array + _u16(self.data, record + 2))
            marks.append((mark_class, anchor))
        ligature_count = _u16(self.data, ligature_array)
        ligatures = []
        for index in range(ligature_count):
            attach = ligature_array + _u16(self.data, ligature_array + 2 + index * 2)
            components = _u16(self.data, attach)
            anchors = []
            for component in range(components):
                record = attach + 2 + component * class_count * 2
                per_class = []
                for class_index in range(class_count):
                    offset = _u16(self.data, record + class_index * 2)
                    per_class.append(self._anchor(attach + offset) if offset else (0, 0))
                anchors.append(per_class)
            ligatures.append(anchors)
        mark_list = sorted(mark_coverage)
        ligature_list = sorted(ligature_coverage)
        for mark_index, mark_gid in enumerate(mark_list):
            if mark_index >= len(marks):
                break
            mark_class, (mark_x, mark_y) = marks[mark_index]
            if mark_class >= class_count:
                continue
            self.mark_glyphs.add(mark_gid)
            for ligature_index, ligature_gid in enumerate(ligature_list):
                if ligature_index >= len(ligatures):
                    break
                components = ligatures[ligature_index]
                if not components:
                    continue
                base_x, base_y = components[-1][mark_class]
                self.mark_ligature_positions[(ligature_gid, mark_gid)] = (
                    base_x - mark_x, base_y - mark_y)

    def _parse_mark_base_subtable(self, sub):
        if _u16(self.data, sub) != 1:
            return
        mark_coverage = self._coverage(sub + _u16(self.data, sub + 2))
        base_coverage = self._coverage(sub + _u16(self.data, sub + 4))
        class_count = _u16(self.data, sub + 6)
        mark_array = sub + _u16(self.data, sub + 8)
        base_array = sub + _u16(self.data, sub + 10)
        mark_count = _u16(self.data, mark_array)
        marks = []
        for index in range(mark_count):
            record = mark_array + 2 + index * 4
            mark_class = _u16(self.data, record)
            anchor = self._anchor(mark_array + _u16(self.data, record + 2))
            marks.append((mark_class, anchor))
        base_count = _u16(self.data, base_array)
        bases = []
        for index in range(base_count):
            record = base_array + 2 + index * class_count * 2
            anchors = []
            for class_index in range(class_count):
                offset = _u16(self.data, record + class_index * 2)
                anchors.append(self._anchor(base_array + offset) if offset else (0, 0))
            bases.append(anchors)
        mark_list = sorted(mark_coverage)
        base_list = sorted(base_coverage)
        for mark_index, mark_gid in enumerate(mark_list):
            if mark_index >= len(marks):
                break
            mark_class, (mark_x, mark_y) = marks[mark_index]
            if mark_class >= class_count:
                continue
            self.mark_glyphs.add(mark_gid)
            for base_index, base_gid in enumerate(base_list):
                if base_index >= len(bases):
                    break
                self.base_glyphs.add(base_gid)
                base_x, base_y = bases[base_index][mark_class]
                self.mark_positions[(base_gid, mark_gid)] = (base_x - mark_x,
                                                             base_y - mark_y)

    def _classdef(self, offset):
        mapping = {}
        fmt = _u16(self.data, offset)
        if fmt == 1:
            start = _u16(self.data, offset + 2)
            count = _u16(self.data, offset + 4)
            for index in range(count):
                mapping[start + index] = _u16(self.data, offset + 6 + index * 2)
        elif fmt == 2:
            count = _u16(self.data, offset + 2)
            for index in range(count):
                start = _u16(self.data, offset + 4 + index * 6)
                end = _u16(self.data, offset + 6 + index * 6)
                value = _u16(self.data, offset + 8 + index * 6)
                for glyph in range(start, end + 1):
                    mapping[glyph] = value
        return mapping

    def _parse_class_pair_subtable(self, sub):
        coverage = self._coverage(sub + _u16(self.data, sub + 2))
        format1 = _u16(self.data, sub + 4)
        format2 = _u16(self.data, sub + 6)
        class1 = self._classdef(sub + _u16(self.data, sub + 8))
        class2 = self._classdef(sub + _u16(self.data, sub + 10))
        count1 = _u16(self.data, sub + 12)
        count2 = _u16(self.data, sub + 14)
        record_size = self._value_size(format1) + self._value_size(format2)
        position = sub + 16
        matrix = []
        for _first in range(count1):
            row = []
            for _second in range(count2):
                advance = 0
                if format1 & 0x0004:
                    advance = _s16(self.data, position + 2 * bin(format1 & 0x0007).count("1"))
                row.append(advance)
                position += record_size
            matrix.append(row)
        self.gpos_class_tables.append((coverage, class1, class2, matrix))

    @staticmethod
    def _value_size(format_flags):
        size = 0
        for bit in (1, 2, 4, 8):
            if format_flags & bit:
                size += 2
        if format_flags & 0x10:
            size += 2
        if format_flags & 0x20:
            size += 2
        if format_flags & 0x40:
            size += 2
        if format_flags & 0x80:
            size += 2
        return size

    def _parse_pair_subtable(self, sub):
        if _u16(self.data, sub) == 2:
            self._parse_class_pair_subtable(sub)
            return
        if _u16(self.data, sub) != 1:
            return
        coverage = self._coverage(sub + _u16(self.data, sub + 2))
        format1 = _u16(self.data, sub + 4)
        format2 = _u16(self.data, sub + 6)
        set_count = _u16(self.data, sub + 8)
        record_size = 2 + self._value_size(format1) + self._value_size(format2)
        for index in range(set_count):
            set_offset = sub + _u16(self.data, sub + 10 + index * 2)
            pair_count = _u16(self.data, set_offset)
            position = set_offset + 2
            for _pair in range(pair_count):
                second = _u16(self.data, position)
                position += 2
                value1 = position
                position += self._value_size(format1)
                value2 = position
                position += self._value_size(format2)
                advance = 0
                if format1 & 0x0004:
                    advance = _s16(self.data, value1 + 2 * bin(format1 & 0x0007).count("1"))
                if advance:
                    # coverage index maps to first glyph via coverage table
                    first = None
                    if index < len(coverage):
                        first = sorted(coverage)[index]
                    if first is not None:
                        self.gpos_pairs[(first, second)] = advance
            # second value record is currently ignored (placement)

    def glyph_id(self, character):
        return self.cmap.get(ord(character), 0)

    def advance(self, glyph_id):
        if self.num_hmetrics <= 0:
            return 0
        index = min(glyph_id, self.num_hmetrics - 1)
        return _u16(self.data, self._hmtx_offset + index * 4) * self.scale

    def _outline(self, glyph_id):
        if glyph_id in self._outline_cache:
            return self._outline_cache[glyph_id]
        offset = self._loca[glyph_id] if glyph_id < len(self._loca) else 0
        if offset == 0 or "glyf" not in self.tables:
            self._outline_cache[glyph_id] = []
            return []
        start = self.tables["glyf"][0] + offset
        contours = _s16(self.data, start)
        if contours < 0:
            outlines = self._composite(glyph_id, start)
            self._outline_cache[glyph_id] = outlines
            return outlines
        end_points = [_u16(self.data, start + 10 + index * 2)
                      for index in range(contours)]
        instruction_length = _u16(self.data, start + 10 + contours * 2)
        position = start + 12 + contours * 2 + instruction_length
        point_count = end_points[-1] + 1 if end_points else 0
        flags = []
        while len(flags) < point_count:
            flag = self.data[position]
            position += 1
            flags.append(flag)
            if flag & 8:
                repeat = self.data[position]
                position += 1
                flags.extend([flag] * repeat)
        flags = flags[:point_count]
        xs = []
        value = 0
        for flag in flags:
            if flag & 2:
                delta = self.data[position]
                position += 1
                value += delta if flag & 16 else -delta
            elif not flag & 16:
                value += _s16(self.data, position)
                position += 2
            xs.append(value)
        ys = []
        value = 0
        for flag in flags:
            if flag & 4:
                delta = self.data[position]
                position += 1
                value += delta if flag & 32 else -delta
            elif not flag & 32:
                value += _s16(self.data, position)
                position += 2
            ys.append(value)
        points = [(xs[index], ys[index], bool(flags[index] & 1))
                  for index in range(point_count)]
        outlines = []
        first = 0
        for end in end_points:
            contour = points[first:end + 1]
            first = end + 1
            if not contour:
                continue
            outlines.append(self._flatten(contour))
        self._outline_cache[glyph_id] = outlines
        return outlines

    def _composite(self, glyph_id, start):
        guard = getattr(self, "_composite_guard", set())
        if glyph_id in guard:
            return []
        self._composite_guard = guard | {glyph_id}
        position = start + 10
        outlines = []
        try:
            while True:
                flags = _u16(self.data, position)
                component = _u16(self.data, position + 2)
                position += 4
                if flags & 0x0001:
                    dx = _s16(self.data, position)
                    dy = _s16(self.data, position + 2)
                    position += 4
                else:
                    dx = struct.unpack_from(">b", self.data, position)[0]
                    dy = struct.unpack_from(">b", self.data, position + 1)[0]
                    position += 2
                if not flags & 0x0002:
                    dx = dy = 0
                if flags & 0x0008:
                    position += 2
                elif flags & 0x0040:
                    position += 4
                elif flags & 0x0080:
                    position += 8
                for contour in self._outline(component):
                    outlines.append([(x + dx, y + dy) for x, y in contour])
                if not flags & 0x0020:
                    break
        except Exception:
            pass
        self._composite_guard = guard
        return outlines

    @staticmethod
    def _flatten(contour):
        if not contour:
            return []
        on = [point for point in contour if point[2]]
        if not on:
            start = ((contour[0][0] + contour[-1][0]) / 2,
                     (contour[0][1] + contour[-1][1]) / 2)
        elif contour[0][2]:
            start = (contour[0][0], contour[0][1])
        else:
            start = ((contour[0][0] + contour[-1][0]) / 2,
                     (contour[0][1] + contour[-1][1]) / 2)
        polygon = [start]
        current = start
        index = 0
        count = len(contour)
        while index < count:
            point = contour[index]
            if point[2]:
                polygon.append((point[0], point[1]))
                current = (point[0], point[1])
                index += 1
                continue
            control = (point[0], point[1])
            following = contour[(index + 1) % count]
            if following[2]:
                end = (following[0], following[1])
                advance = 2
            else:
                end = ((point[0] + following[0]) / 2,
                       (point[1] + following[1]) / 2)
                advance = 1
            for step in range(1, 7):
                t = step / 6
                x = ((1 - t) ** 2 * current[0] + 2 * (1 - t) * t * control[0] +
                     t * t * end[0])
                y = ((1 - t) ** 2 * current[1] + 2 * (1 - t) * t * control[1] +
                     t * t * end[1])
                polygon.append((x, y))
            current = end
            index += advance
        return polygon

    def kerning(self, first, second):
        value = self.gpos_pairs.get((first, second))
        if value is not None:
            return value
        for coverage, class1, class2, matrix in self.gpos_class_tables:
            if first in coverage:
                row = matrix[class1.get(first, 0)]
                return row[class2.get(second, 0)]
        return self.kern.get((first, second), 0)

    def positioned(self, text):
        glyphs = self.shape(text)
        output = []
        base = None
        mark = None
        for glyph in glyphs:
            offset = (0, 0)
            if glyph in self.mark_glyphs:
                if mark is not None:
                    offset = self.mark_mark_positions.get((mark, glyph), (0, 0))
                elif base is not None:
                    offset = self.mark_ligature_positions.get((base, glyph))
                    if offset is None:
                        offset = self.mark_positions.get((base, glyph), (0, 0))
                mark = glyph
            else:
                base = glyph
                mark = None
            output.append((glyph, offset[0], offset[1]))
        return output

    @staticmethod
    def _runs(text):
        buffer = ""
        for character in str(text):
            if character.isspace():
                if buffer:
                    yield buffer
                    buffer = ""
                yield character
            else:
                buffer += character
        if buffer:
            yield buffer

    def draw(self, canvas, text, x, y, color=None):
        color = color or Color(235, 240, 250)
        cursor = x
        baseline = y + self.ascent * self.scale
        previous = None
        for run in self._runs(text):
            if run == "\n":
                cursor = x
                baseline += self.size
                previous = None
                continue
            if run.isspace():
                cursor += self.advance(self.glyph_id(run))
                previous = None
                continue
            for glyph_id in self.shape(run):
                if previous is not None:
                    cursor += self.kerning(previous, glyph_id) * self.scale
                previous = glyph_id
                for contour in self._outline(glyph_id):
                    points = [(cursor + px * self.scale,
                               baseline - py * self.scale) for px, py in contour]
                    if len(points) >= 3:
                        canvas.fill_polygon(points, color)
                cursor += self.advance(glyph_id)
        return cursor

    def measure(self, text):
        total = 0
        previous = None
        for run in self._runs(text):
            if run == "\n":
                continue
            if run.isspace():
                total += self.advance(self.glyph_id(run))
                previous = None
                continue
            for glyph in self.shape(run):
                if previous is not None:
                    total += self.kerning(previous, glyph) * self.scale
                total += self.advance(glyph)
                previous = glyph
        return total
