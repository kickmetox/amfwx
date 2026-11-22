"""AMFWX multi-line text editor with selection, undo/redo and clipboard."""

from __future__ import annotations

from .canvas import Color, Rect
from .clipboard import get_text as clipboard_get, set_text as clipboard_set
from .text import draw_text, measure_text
from .textlayout import TextLayout
from .widgets import (
    VK_BACK, VK_DELETE, VK_DOWN, VK_END, VK_HOME, VK_LEFT, VK_RETURN,
    VK_RIGHT, VK_UP, Widget,
)

VK_A = 65
VK_C = 67
VK_V = 86
VK_X = 88
VK_Y = 89
VK_Z = 90
CTRL = 2
SHIFT = 1


class TextEdit(Widget):
    focusable = True

    def __init__(self, text="", font=None, on_change=None):
        super().__init__()
        self._text = str(text)
        self.cursor = len(self._text)
        self.anchor = self.cursor
        self.font = font
        self.on_change = on_change
        self.layout = TextLayout(font, max_width=600) if font else None
        self._undo = []
        self._redo = []
        self._dragging = False

    def text(self):
        return self._text

    def set_text(self, text):
        self._record()
        self._text = str(text)
        self.cursor = self.anchor = min(self.cursor, len(self._text))
        self._changed()

    def selection_range(self):
        return min(self.anchor, self.cursor), max(self.anchor, self.cursor)

    def has_selection(self):
        return self.anchor != self.cursor

    def selected_text(self):
        start, end = self.selection_range()
        return self._text[start:end]

    def size_hint(self):
        return (360, 180)

    def _record(self):
        self._undo.append((self._text, self.cursor, self.anchor))
        self._redo.clear()

    def _replace(self, start, end, text, cursor=None):
        self._record()
        self._text = self._text[:start] + text + self._text[end:]
        self.cursor = start + len(text) if cursor is None else cursor
        self.anchor = self.cursor
        self._changed()

    def undo(self):
        if not self._undo:
            return
        self._redo.append((self._text, self.cursor, self.anchor))
        self._text, self.cursor, self.anchor = self._undo.pop()
        self._changed()

    def redo(self):
        if not self._redo:
            return
        self._undo.append((self._text, self.cursor, self.anchor))
        self._text, self.cursor, self.anchor = self._redo.pop()
        self._changed()

    def select_all(self):
        self.anchor = 0
        self.cursor = len(self._text)
        self.update()

    def paint(self, canvas):
        theme = self.theme()
        canvas.rounded_rect(self.rect, theme.radius, theme.surface)
        canvas.draw_rect(self.rect, theme.focus if self.focused else theme.border,
                         2 if self.focused else 1)
        self._paint_selection(canvas, theme)
        if self.layout is not None:
            self.layout.max_width = max(20, self.rect.w - 12)
            self.layout.draw(canvas, self._text, self.rect.x + 6,
                             self.rect.y + 6, theme.text)
        else:
            y = self.rect.y + 6
            for line in self._text.split("\n"):
                draw_text(canvas, line, self.rect.x + 6, y, theme.text, 2)
                y += 18
        if self.focused:
            x, y = self._cursor_xy()
            canvas.fill_rect(Rect(x, y, 2, 16), theme.text)

    def _layout_lines(self):
        if self.layout is not None:
            self.layout.max_width = max(20, self.rect.w - 12)
            return [line.text for line in self.layout.lines(self._text)]
        return self._text.split("\n")

    def _measure_prefix(self, text):
        if self.layout is not None:
            return self.layout._measure(text)
        return measure_text(text, 2)

    def _paint_selection(self, canvas, theme):
        if not self.has_selection():
            return
        start, end = self.selection_range()
        offset = 0
        y = self.rect.y + 6
        for line in self._layout_lines():
            line_start = offset
            line_end = offset + len(line)
            a = max(start, line_start)
            b = min(end, line_end)
            if a < b:
                before = line[:a - line_start]
                selected = line[a - line_start:b - line_start]
                x = self.rect.x + 6 + self._measure_prefix(before)
                width = self._measure_prefix(selected)
                height = self.layout.line_height if self.layout else 18
                canvas.fill_rect(Rect(x, y, max(1, width), height),
                                 theme.accent.with_alpha(80))
            offset = line_end + 1
            y += self.layout.line_height if self.layout else 18
            if line_end >= end:
                break

    def _cursor_xy(self):
        before = self._text[:self.cursor]
        line = before.count("\n")
        column = before.rsplit("\n", 1)[-1]
        x = self.rect.x + 6 + self._measure_prefix(column)
        height = self.layout.line_height if self.layout else 18
        y = self.rect.y + 6 + line * height
        return x, y

    def _index_from_point(self, x, y):
        lines = self._layout_lines()
        height = self.layout.line_height if self.layout else 18
        line_index = max(0, min(len(lines) - 1,
                               int((y - self.rect.y - 6) // height)))
        line = lines[line_index]
        offset = 0
        for line_number, content in enumerate(lines):
            if line_number == line_index:
                break
            offset += len(content) + 1
        target = max(0, x - self.rect.x - 6)
        best = 0
        for index in range(len(line) + 1):
            if self._measure_prefix(line[:index]) >= target:
                best = index
                break
            best = index
        return offset + best

    def mouse_down(self, x, y, button="left"):
        index = self._index_from_point(x, y)
        self.cursor = index
        self.anchor = index
        self._dragging = True

    def mouse_move(self, x, y):
        if self._dragging:
            self.cursor = self._index_from_point(x, y)

    def mouse_up(self, x, y, button="left"):
        self._dragging = False

    def _move(self, index, extend=False):
        self.cursor = max(0, min(len(self._text), index))
        if not extend:
            self.anchor = self.cursor

    def key_down(self, key, modifiers=0):
        ctrl = bool(modifiers & CTRL)
        shift = bool(modifiers & SHIFT)
        if ctrl and key == VK_A:
            self.select_all()
            return
        if ctrl and key == VK_C:
            if self.has_selection():
                clipboard_set(self.selected_text())
            return
        if ctrl and key == VK_X:
            if self.has_selection():
                clipboard_set(self.selected_text())
                start, end = self.selection_range()
                self._replace(start, end, "")
            return
        if ctrl and key == VK_V:
            text = clipboard_get()
            if text:
                start, end = self.selection_range()
                self._replace(start, end, text)
            return
        if ctrl and key == VK_Z:
            self.undo()
            return
        if ctrl and key == VK_Y:
            self.redo()
            return
        start, end = self.selection_range()
        if key == VK_LEFT:
            self._move(start if self.has_selection() else self.cursor - 1, shift)
        elif key == VK_RIGHT:
            self._move(end if self.has_selection() else self.cursor + 1, shift)
        elif key == VK_HOME:
            line_start = self._text.rfind("\n", 0, self.cursor) + 1
            self._move(line_start, shift)
        elif key == VK_END:
            line_end = self._text.find("\n", self.cursor)
            self._move(len(self._text) if line_end < 0 else line_end, shift)
        elif key in (VK_UP, VK_DOWN):
            self._vertical(key == VK_UP, shift)
        elif key == VK_BACK:
            if self.has_selection():
                self._replace(start, end, "")
            elif self.cursor > 0:
                self._replace(self.cursor - 1, self.cursor, "")
        elif key == VK_DELETE:
            if self.has_selection():
                self._replace(start, end, "")
            elif self.cursor < len(self._text):
                self._replace(self.cursor, self.cursor + 1, "")
        elif key == VK_RETURN:
            self._replace(start, end, "\n")

    def _vertical(self, up, extend=False):
        before = self._text[:self.cursor]
        line = before.count("\n")
        column = len(before.rsplit("\n", 1)[-1])
        if up:
            if line == 0:
                return
            previous_end = self._text.rfind("\n", 0, self.cursor)
            previous_start = self._text.rfind("\n", 0, previous_end) + 1
            target = min(previous_start + column, previous_end)
        else:
            end = self._text.find("\n", self.cursor)
            if end < 0:
                return
            next_start = end + 1
            next_end = self._text.find("\n", next_start)
            target = min(next_start + column,
                         len(self._text) if next_end < 0 else next_end)
        self._move(target, extend)

    def char_input(self, character):
        if character.isprintable() or character == "\n":
            start, end = self.selection_range()
            self._replace(start, end, character)

    def select_range(self, start, end):
        self.anchor = max(0, min(len(self._text), start))
        self.cursor = max(0, min(len(self._text), end))
        window = self.window()
        if window is not None and hasattr(window, "set_focus"):
            window.set_focus(self)

    def find(self, needle, start=None, case_sensitive=False):
        needle = str(needle)
        if not needle:
            return -1
        haystack = self._text if case_sensitive else self._text.lower()
        target = needle if case_sensitive else needle.lower()
        if start is None:
            start = self.cursor
        index = haystack.find(target, max(0, start))
        if index < 0:
            return -1
        self.select_range(index, index + len(needle))
        return index

    def find_next(self, needle, case_sensitive=False):
        start = self.cursor
        index = self.find(needle, start, case_sensitive)
        if index < 0 and start > 0:
            index = self.find(needle, 0, case_sensitive)
        return index

    def replace_all(self, needle, replacement, case_sensitive=False):
        needle = str(needle)
        if not needle:
            return 0
        source = self._text if case_sensitive else self._text.lower()
        target = needle if case_sensitive else needle.lower()
        count = source.count(target)
        if count:
            self._record()
            if case_sensitive:
                self._text = self._text.replace(needle, str(replacement))
            else:
                import re
                self._text = re.sub(re.escape(needle), str(replacement),
                                    self._text, flags=re.IGNORECASE)
            self.cursor = self.anchor = min(self.cursor, len(self._text))
            self._changed()
        return count

    def _changed(self):
        if self.on_change:
            self.on_change(self._text)
        window = self.window()
        if window is not None and hasattr(window, "_uia_value_changed"):
            window._uia_value_changed(self)
