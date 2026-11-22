"""Text layout: word wrap, line breaks and font fallback."""

from __future__ import annotations

from dataclasses import dataclass

from .canvas import Color


@dataclass
class Line:
    text: str
    width: int


from .arabic import arabic_shape
from .bidi import bidi_reorder


class TextLayout:
    def __init__(self, font, fallback_fonts=None, max_width=400,
                 line_spacing=1.25):
        self.font = font
        self.fallbacks = list(fallback_fonts or [])
        self.max_width = max(1, int(max_width))
        self.line_spacing = line_spacing

    def _font_for(self, character):
        if self.font is not None and self.font.glyph_id(character):
            return self.font
        for font in self.fallbacks:
            if font.glyph_id(character):
                return font
        return self.font

    def _measure(self, text):
        return sum(self._font_for(character).advance(
            self._font_for(character).glyph_id(character))
            for character in text)

    def lines(self, text):
        result = []
        for paragraph in str(text).split("\n"):
            paragraph = bidi_reorder(arabic_shape(paragraph))
            current = ""
            width = 0
            for character in paragraph:
                char_width = self._font_for(character).advance(
                    self._font_for(character).glyph_id(character))
                if current and width + char_width > self.max_width:
                    split = current.rfind(" ")
                    if split > 0:
                        result.append(Line(current[:split], int(width)))
                        current = current[split + 1:]
                        width = self._measure(current)
                    else:
                        result.append(Line(current, int(width)))
                        current = ""
                        width = 0
                current += character
                width += char_width
            result.append(Line(current, int(width)))
        return result

    @property
    def line_height(self):
        size = getattr(self.font, "size", 16) if self.font else 16
        return int(size * self.line_spacing)

    def height(self, text):
        return max(1, len(self.lines(text))) * self.line_height

    def draw(self, canvas, text, x, y, color=None, clip=None):
        color = color or Color(235, 240, 250)
        cursor_y = int(y)
        for line in self.lines(text):
            cursor_x = int(x)
            for character in line.text:
                font = self._font_for(character)
                if font is None:
                    continue
                font.draw(canvas, character, cursor_x, cursor_y, color)
                cursor_x += font.advance(font.glyph_id(character))
            cursor_y += self.line_height
        return cursor_y
