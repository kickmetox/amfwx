"""AMFWX software rasterizer: BGRA canvas, no GDI+ drawing."""

from __future__ import annotations

import math
import struct
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255

    @classmethod
    def from_hex(cls, value):
        value = str(value).lstrip("#")
        if len(value) == 6:
            return cls(int(value[0:2], 16), int(value[2:4], 16),
                       int(value[4:6], 16))
        if len(value) == 8:
            return cls(int(value[0:2], 16), int(value[2:4], 16),
                       int(value[4:6], 16), int(value[6:8], 16))
        raise ValueError("color must be #rrggbb or #rrggbbaa")

    def with_alpha(self, alpha):
        return Color(self.r, self.g, self.b, int(alpha))

    def to_bgra(self):
        return bytes((self.b, self.g, self.r, self.a))


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y + self.h

    def contains(self, x, y):
        return self.x <= x < self.right and self.y <= y < self.bottom


class Canvas:
    def __init__(self, width, height, background=Color(24, 26, 32)):
        self.width = max(1, int(width))
        self.height = max(1, int(height))
        self.data = bytearray(self.width * self.height * 4)
        self._clip = (0, 0, self.width, self.height)
        self._clip_stack = []
        self.clear(background)

    def push_clip(self, rect):
        self._clip_stack.append(self._clip)
        x0 = max(self._clip[0], int(rect.x))
        y0 = max(self._clip[1], int(rect.y))
        x1 = min(self._clip[2], int(math.ceil(rect.right)))
        y1 = min(self._clip[3], int(math.ceil(rect.bottom)))
        self._clip = (x0, y0, max(x0, x1), max(y0, y1))

    def pop_clip(self):
        if self._clip_stack:
            self._clip = self._clip_stack.pop()

    def _in_clip(self, x, y):
        return (self._clip[0] <= x < self._clip[2] and
                self._clip[1] <= y < self._clip[3])

    def resize(self, width, height):
        width, height = max(1, int(width)), max(1, int(height))
        if (width, height) == (self.width, self.height):
            return
        self.width, self.height = width, height
        self.data = bytearray(width * height * 4)

    def scaled(self, width, height, bilinear=True):
        width, height = max(1, int(width)), max(1, int(height))
        output = Canvas(width, height)
        if not bilinear:
            for y in range(height):
                for x in range(width):
                    output.set_pixel(x, y, self.pixel(
                        int(x * self.width / width),
                        int(y * self.height / height)))
            return output
        for y in range(height):
            source_y = (y + 0.5) * self.height / height - 0.5
            y0 = max(0, min(self.height - 1, int(source_y)))
            y1 = min(self.height - 1, y0 + 1)
            fy = source_y - int(source_y)
            for x in range(width):
                source_x = (x + 0.5) * self.width / width - 0.5
                x0 = max(0, min(self.width - 1, int(source_x)))
                x1 = min(self.width - 1, x0 + 1)
                fx = source_x - int(source_x)
                c00, c10 = self.pixel(x0, y0), self.pixel(x1, y0)
                c01, c11 = self.pixel(x0, y1), self.pixel(x1, y1)
                channels = []
                for attr in ("r", "g", "b", "a"):
                    top = getattr(c00, attr) * (1 - fx) + getattr(c10, attr) * fx
                    bottom = getattr(c01, attr) * (1 - fx) + getattr(c11, attr) * fx
                    channels.append(int(top * (1 - fy) + bottom * fy))
                output.set_pixel(x, y, Color(*channels))
        return output

    def crop(self, x, y, width, height):
        output = Canvas(width, height)
        for oy in range(height):
            for ox in range(width):
                output.set_pixel(ox, oy, self.pixel(x + ox, y + oy))
        return output

    def thumbnail(self, maximum):
        maximum = max(1, int(maximum))
        scale = min(maximum / self.width, maximum / self.height, 1.0)
        return self.scaled(max(1, int(self.width * scale)),
                           max(1, int(self.height * scale)))

    def clear(self, color=Color(24, 26, 32)):
        self.data[:] = color.to_bgra() * (self.width * self.height)

    def _index(self, x, y):
        return (int(y) * self.width + int(x)) * 4

    def pixel(self, x, y):
        x, y = int(x), int(y)
        if not (0 <= x < self.width and 0 <= y < self.height):
            return Color(0, 0, 0, 0)
        i = self._index(x, y)
        return Color(self.data[i + 2], self.data[i + 1], self.data[i],
                     self.data[i + 3])

    def set_pixel(self, x, y, color):
        x, y = int(x), int(y)
        if self._in_clip(x, y):
            i = self._index(x, y)
            self.data[i:i + 4] = color.to_bgra()

    def blend_pixel(self, x, y, color):
        x, y = int(x), int(y)
        if not self._in_clip(x, y):
            return
        alpha = max(0, min(255, color.a))
        if alpha == 0:
            return
        if alpha == 255:
            self.set_pixel(x, y, color)
            return
        i = self._index(x, y)
        inverse = 255 - alpha
        self.data[i] = (color.b * alpha + self.data[i] * inverse) // 255
        self.data[i + 1] = (color.g * alpha + self.data[i + 1] * inverse) // 255
        self.data[i + 2] = (color.r * alpha + self.data[i + 2] * inverse) // 255
        self.data[i + 3] = min(255, alpha + self.data[i + 3] * inverse // 255)

    def fill_rect(self, rect, color):
        x0 = max(0, int(rect.x))
        y0 = max(0, int(rect.y))
        x1 = min(self.width, int(math.ceil(rect.right)))
        y1 = min(self.height, int(math.ceil(rect.bottom)))
        x0 = max(x0, self._clip[0])
        y0 = max(y0, self._clip[1])
        x1 = min(x1, self._clip[2])
        y1 = min(y1, self._clip[3])
        if x0 >= x1 or y0 >= y1:
            return
        if color.a == 255:
            row = color.to_bgra()
            for y in range(y0, y1):
                start = self._index(x0, y)
                end = self._index(x1, y)
                self.data[start:end] = row * (x1 - x0)
        else:
            for y in range(y0, y1):
                for x in range(x0, x1):
                    self.blend_pixel(x, y, color)

    def draw_rect(self, rect, color, width=1):
        width = max(1, int(width))
        self.fill_rect(Rect(rect.x, rect.y, rect.w, width), color)
        self.fill_rect(Rect(rect.x, rect.bottom - width, rect.w, width), color)
        self.fill_rect(Rect(rect.x, rect.y, width, rect.h), color)
        self.fill_rect(Rect(rect.right - width, rect.y, width, rect.h), color)

    def line(self, x0, y0, x1, y1, color, width=1):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        error = dx + dy
        radius = max(0, int(width) // 2)
        while True:
            if radius:
                self.fill_circle(x0, y0, radius, color)
            else:
                self.blend_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            twice = 2 * error
            if twice >= dy:
                error += dy
                x0 += sx
            if twice <= dx:
                error += dx
                y0 += sy

    def polyline(self, points, color, width=1):
        for first, second in zip(points, points[1:]):
            self.line(first[0], first[1], second[0], second[1], color, width)

    def fill_polygon(self, points, color):
        if len(points) < 3:
            return
        ys = [point[1] for point in points]
        y_min = max(0, int(math.floor(min(ys))))
        y_max = min(self.height - 1, int(math.ceil(max(ys))))
        for y in range(y_min, y_max + 1):
            center = y + 0.5
            nodes = []
            for index in range(len(points)):
                x1, y1 = points[index]
                x2, y2 = points[(index + 1) % len(points)]
                if (y1 <= center < y2) or (y2 <= center < y1):
                    t = (center - y1) / (y2 - y1) if y2 != y1 else 0
                    nodes.append(x1 + t * (x2 - x1))
            nodes.sort()
            for index in range(0, len(nodes) - 1, 2):
                start = max(0, int(math.ceil(nodes[index])))
                end = min(self.width - 1, int(math.floor(nodes[index + 1])))
                for x in range(start, end + 1):
                    self.blend_pixel(x, y, color)

    def fill_circle(self, cx, cy, radius, color):
        radius = abs(float(radius))
        if radius < 0.5:
            self.blend_pixel(cx, cy, color)
            return
        x0 = int(math.floor(cx - radius))
        x1 = int(math.ceil(cx + radius))
        y0 = int(math.floor(cy - radius))
        y1 = int(math.ceil(cy + radius))
        radius2 = radius * radius
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= radius2:
                    self.blend_pixel(x, y, color)

    def fill_circle_aa(self, cx, cy, radius, color):
        radius = abs(float(radius))
        x0, x1 = int(math.floor(cx - radius)), int(math.ceil(cx + radius))
        y0, y1 = int(math.floor(cy - radius)), int(math.ceil(cy + radius))
        radius2 = radius * radius
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                coverage = 0
                for sy in (0.25, 0.75):
                    for sx in (0.25, 0.75):
                        if (x + sx - cx) ** 2 + (y + sy - cy) ** 2 <= radius2:
                            coverage += 1
                if coverage:
                    self.blend_pixel(x, y, color.with_alpha(
                        int(color.a * coverage / 4)))

    def rounded_rect(self, rect, radius, color):
        radius = max(0, min(float(radius), rect.w / 2, rect.h / 2))
        self.fill_rect(Rect(rect.x + radius, rect.y, rect.w - 2 * radius,
                            rect.h), color)
        self.fill_rect(Rect(rect.x, rect.y + radius, rect.w,
                            rect.h - 2 * radius), color)
        self.fill_circle_aa(rect.x + radius, rect.y + radius, radius, color)
        self.fill_circle_aa(rect.right - radius, rect.y + radius, radius, color)
        self.fill_circle_aa(rect.x + radius, rect.bottom - radius, radius, color)
        self.fill_circle_aa(rect.right - radius, rect.bottom - radius, radius, color)

    def draw_image_xy(self, x, y, image):
        self.blit(image, int(x), int(y))

    def draw_image(self, x, y, image):
        self.draw_image_xy(x, y, image)

    def blit(self, other, x=0, y=0):
        for oy in range(other.height):
            for ox in range(other.width):
                color = other.pixel(ox, oy)
                if color.a:
                    self.blend_pixel(x + ox, y + oy, color)

    @classmethod
    def from_clipboard_image(cls):
        from .clipboard import get_image
        image = get_image()
        return image

    @classmethod
    def from_jpeg(cls, path):
        from .jpeg import decode_jpeg
        width, height, pixels = decode_jpeg(Path(path).read_bytes())
        canvas = cls(width, height)
        canvas.data[:] = pixels
        return canvas

    def save_png(self, path):
        from .png import encode_png
        Path(path).write_bytes(encode_png(self.width, self.height, self.data))
        return path

    @classmethod
    def from_png(cls, path):
        from .png import decode_png
        width, height, pixels = decode_png(Path(path).read_bytes())
        canvas = cls(width, height)
        canvas.data[:] = pixels
        return canvas

    def save_pdf(self, path):
        from .pdf import canvas_to_pdf
        return canvas_to_pdf(self, path)

    def save_bmp(self, path):
        row_size = (self.width * 3 + 3) & ~3
        pixel_size = row_size * self.height
        header = struct.pack("<2sIHHI", b"BM", 54 + pixel_size, 0, 0, 54)
        info = struct.pack("<IiiHHIIiiII", 40, self.width, self.height, 1, 24,
                           0, pixel_size, 2835, 2835, 0, 0)
        rows = []
        for y in range(self.height - 1, -1, -1):
            row = bytearray()
            for x in range(self.width):
                color = self.pixel(x, y)
                row.extend((color.b, color.g, color.r))
            row.extend(b"\0" * (row_size - len(row)))
            rows.append(bytes(row))
        with open(path, "wb") as handle:
            handle.write(header)
            handle.write(info)
            for row in rows:
                handle.write(row)
        return path
