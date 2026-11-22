"""Small HTML-subset RichText widget."""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser

from .canvas import Rect
from .text import draw_text, measure_text
from .widgets import Widget


@dataclass
class Span:
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    link: str = ""


@dataclass
class Block:
    kind: str = "p"
    spans: list = field(default_factory=list)


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.current = Block()
        self.bold = 0
        self.italic = 0
        self.underline = 0
        self.link = ""

    def _flush(self):
        if self.current.spans:
            self.blocks.append(self.current)
        self.current = Block()

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in ("p", "div", "h1", "h2", "h3", "li"):
            self._flush()
            self.current.kind = tag
            if tag == "li":
                self.current.spans.append(Span("\u2022 "))
        elif tag == "br":
            self.current.spans.append(Span("\n"))
        elif tag == "b" or tag == "strong":
            self.bold += 1
        elif tag == "i" or tag == "em":
            self.italic += 1
        elif tag == "u":
            self.underline += 1
        elif tag == "a":
            self.link = dict(attrs).get("href", "")
            self.underline += 1

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ("p", "div", "h1", "h2", "h3", "li"):
            self._flush()
        elif tag in ("b", "strong"):
            self.bold = max(0, self.bold - 1)
        elif tag in ("i", "em"):
            self.italic = max(0, self.italic - 1)
        elif tag == "u":
            self.underline = max(0, self.underline - 1)
        elif tag == "a":
            self.link = ""
            self.underline = max(0, self.underline - 1)

    def handle_data(self, data):
        if data:
            self.current.spans.append(Span(
                data, bool(self.bold), bool(self.italic),
                bool(self.underline), self.link))

    def close(self):
        super().close()
        self._flush()


class RichDocument:
    def __init__(self, html=""):
        self.blocks = []
        self.set_html(html)

    def set_html(self, html):
        parser = _Parser()
        parser.feed(str(html or ""))
        parser.close()
        self.blocks = parser.blocks
        return self

    def plain_text(self):
        return "\n".join("".join(span.text for span in block.spans)
                         for block in self.blocks)

    def _font(self, theme, kind):
        if kind in ("h1", "h2", "h3"):
            from .font import TrueTypeFont
            return None
        return None

    def render(self, canvas, rect, theme, scale=2):
        y = rect.y + 4
        width = max(40, rect.w - 8)
        for block in self.blocks:
            if block.kind in ("h1", "h2", "h3"):
                size = {"h1": 3, "h2": 2, "h3": 2}.get(block.kind, 2)
                color = theme.text
                spacing = 8
            else:
                size = scale
                color = theme.text
                spacing = 4
            tokens = []
            for span in block.spans:
                tokens.extend(self._tokens(span))
            line = []
            line_width = 0
            for token in tokens:
                if token.text == "\n":
                    self._draw_line(canvas, line, rect.x + 4, y,
                                    theme, size)
                    y += measure_text("X", size) + spacing
                    line, line_width = [], 0
                    continue
                token_width = measure_text(token.text, size)
                if line and line_width + token_width > width:
                    self._draw_line(canvas, line, rect.x + 4, y,
                                    theme, size)
                    y += measure_text("X", size) + spacing
                    line, line_width = [], 0
                line.append(token)
                line_width += token_width
            if line:
                self._draw_line(canvas, line, rect.x + 4, y, theme, size)
                y += measure_text("X", size) + spacing
            y += 2
        return y

    def _tokens(self, span):
        result = []
        parts = span.text.split(" ")
        for index, part in enumerate(parts):
            if index:
                result.append(Span(" ", span.bold, span.italic,
                                   span.underline, span.link))
            if part:
                result.append(Span(part, span.bold, span.italic,
                                   span.underline, span.link))
        if not result and span.text:
            result.append(Span(span.text, span.bold, span.italic,
                               span.underline, span.link))
        return result

    def _draw_line(self, canvas, tokens, x, y, theme, scale):
        cursor = x
        for token in tokens:
            color = theme.accent if token.link else theme.text
            draw_text(canvas, token.text, cursor, y, color, scale)
            width = measure_text(token.text, scale)
            if token.underline:
                canvas.fill_rect(Rect(cursor, y + 7 * scale + 1, width, 1),
                                 color)
            if token.bold:
                draw_text(canvas, token.text, cursor + 1, y, color, scale)
            cursor += width


class RichText(Widget):
    def __init__(self, html=""):
        super().__init__()
        self.document = RichDocument(html)

    def set_html(self, html):
        self.document.set_html(html)
        return self

    def text(self):
        return self.document.plain_text()

    def size_hint(self):
        return (360, 120)

    def paint(self, canvas):
        self.document.render(canvas, self.rect, self.theme(), 2)
