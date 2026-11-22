"""AMFWX widgets: inputs, buttons, labels, panels and layouts."""

from __future__ import annotations

from .canvas import Color, Rect
from .text import draw_text, measure_text
from .theme import DARK, Theme

VK_BACK = 8
VK_TAB = 9
VK_RETURN = 13
VK_ESCAPE = 27
VK_SPACE = 32
VK_END = 35
VK_HOME = 36
VK_LEFT = 37
VK_UP = 38
VK_RIGHT = 39
VK_DOWN = 40
VK_DELETE = 46


class Widget:
    focusable = False

    def __init__(self, x=0, y=0, w=0, h=0):
        self.rect = Rect(x, y, w, h)
        self.children = []
        self.parent = None
        self.visible = True
        self.hovered = False
        self.focused = False
        self.enabled = True
        self.tooltip_text = ""
        self.context_menu = None
        self.accessible_name = ""

    def window(self):
        node = self
        while getattr(node, "parent", None) is not None:
            node = node.parent
        if hasattr(node, "hwnd") or "theme" in getattr(node, "__dict__", {}):
            return node
        return None

    def theme(self) -> Theme:
        window = self.window()
        return getattr(window, "theme", DARK) if window is not None else DARK

    def add(self, widget):
        widget.parent = self
        self.children.append(widget)
        return widget

    def size_hint(self):
        return (0, 0)

    def arrange(self, rect):
        self.rect = rect

    def paint(self, canvas):
        for child in self.children:
            if child.visible:
                child.paint(canvas)

    def hit_test(self, x, y):
        if not (self.visible and self.enabled and self.rect.contains(x, y)):
            return None
        for child in reversed(self.children):
            found = child.hit_test(x, y)
            if found is not None:
                return found
        return self

    def local(self, x, y):
        return (x - self.rect.x, y - self.rect.y)

    def mouse_down(self, x, y, button="left"):
        pass

    def mouse_move(self, x, y):
        pass

    def mouse_up(self, x, y, button="left"):
        pass

    def key_down(self, key, modifiers=0):
        pass

    def char_input(self, character):
        pass

    def touch_event(self, event):
        pass

    def gesture_event(self, event):
        pass

    def ime_start(self):
        pass

    def ime_composition(self, text, result=False):
        pass

    def ime_end(self):
        pass

    def drop_files(self, paths, x, y):
        pass

    def set_focused(self, focused):
        self.focused = bool(focused)


class Label(Widget):
    def __init__(self, text="", color=None, scale=2, font=None,
                 label_for=None):
        super().__init__()
        self.text = text
        self.label_for = label_for
        self.color = color
        self.scale = scale
        self.font = font

    def size_hint(self):
        if self.font is not None:
            return (int(self.font.measure(self.text)) + 8,
                    int(self.font.size) + 8)
        return (measure_text(self.text, self.scale) + 8,
                7 * self.scale + 8)

    def paint(self, canvas):
        color = self.color or self.theme().text
        draw_text(canvas, self.text, self.rect.x + 4, self.rect.y + 4,
                  color, self.scale, font=self.font)


class Button(Widget):
    focusable = True

    def __init__(self, text="OK", on_click=None, variant="default"):
        super().__init__()
        self.text = text
        self.on_click = on_click
        self.variant = variant
        self.pressed = False

    def size_hint(self):
        return (measure_text(self.text, 2) + 28, 34)

    def paint(self, canvas):
        theme = self.theme()
        accent = theme.accent if self.variant == "primary" else theme.surface_alt
        if not self.enabled:
            accent = theme.surface_alt
        elif self.pressed:
            accent = accent.with_alpha(170)
        elif self.hovered:
            accent = accent.with_alpha(max(0, accent.a - 15))
        canvas.rounded_rect(self.rect, theme.radius, accent)
        if self.focused:
            canvas.draw_rect(self.rect, theme.focus, 2)
        text_width = measure_text(self.text, 2)
        color = theme.accent_text if self.variant == "primary" else theme.text
        draw_text(canvas, self.text,
                  self.rect.x + (self.rect.w - text_width) / 2,
                  self.rect.y + (self.rect.h - 14) / 2,
                  color, 2)

    def mouse_down(self, x, y, button="left"):
        if self.enabled:
            self.pressed = True

    def mouse_up(self, x, y, button="left"):
        was = self.pressed
        self.pressed = False
        if was and self.rect.contains(x, y):
            self.activate()

    def mouse_move(self, x, y):
        self.hovered = self.rect.contains(x, y)

    def key_down(self, key, modifiers=0):
        if key in (VK_RETURN, VK_SPACE):
            self.activate()

    def activate(self):
        if self.enabled and self.on_click:
            self.on_click()


class Panel(Widget):
    def __init__(self, background=None, radius=0, padding=0):
        super().__init__()
        self.background = background
        self.radius = radius
        self.padding = padding

    def paint(self, canvas):
        theme = self.theme()
        if self.background is not None:
            if self.radius:
                canvas.rounded_rect(self.rect, self.radius, self.background)
            else:
                canvas.fill_rect(self.rect, self.background)
        for child in self.children:
            if child.visible:
                child.paint(canvas)


class LineEdit(Widget):
    focusable = True

    def __init__(self, text="", placeholder=""):
        super().__init__()
        self._text = str(text)
        self.placeholder = placeholder
        self.cursor = len(self._text)
        self.on_change = None
        self.on_enter = None

    def text(self):
        return self._text

    def set_text(self, text):
        self._text = str(text)
        self.cursor = min(self.cursor, len(self._text))
        if self.on_change:
            self.on_change(self._text)

    def size_hint(self):
        return (220, self.theme().control_height)

    def paint(self, canvas):
        theme = self.theme()
        background = theme.surface
        canvas.rounded_rect(self.rect, theme.radius, background)
        border = theme.focus if self.focused else theme.border
        canvas.draw_rect(self.rect, border, 2 if self.focused else 1)
        text = self._text if self._text else self.placeholder
        color = theme.text if self._text else theme.muted
        draw_text(canvas, text, self.rect.x + 8, self.rect.y + 9,
                  color, 2)
        if self.focused:
            width = measure_text(self._text[:self.cursor], 2)
            x = min(self.rect.right - 8, self.rect.x + 8 + width)
            canvas.fill_rect(Rect(x, self.rect.y + 6, 2, self.rect.h - 12),
                             theme.text)

    def mouse_down(self, x, y, button="left"):
        index = 0
        for index in range(len(self._text) + 1):
            if measure_text(self._text[:index], 2) >= x - self.rect.x - 8:
                break
        self.cursor = index

    def key_down(self, key, modifiers=0):
        if key == VK_LEFT:
            self.cursor = max(0, self.cursor - 1)
        elif key == VK_RIGHT:
            self.cursor = min(len(self._text), self.cursor + 1)
        elif key == VK_HOME:
            self.cursor = 0
        elif key == VK_END:
            self.cursor = len(self._text)
        elif key == VK_BACK and self.cursor > 0:
            self._text = self._text[:self.cursor - 1] + self._text[self.cursor:]
            self.cursor -= 1
            self._changed()
        elif key == VK_DELETE and self.cursor < len(self._text):
            self._text = self._text[:self.cursor] + self._text[self.cursor + 1:]
            self._changed()
        elif key == VK_RETURN and self.on_enter:
            self.on_enter()

    def char_input(self, character):
        if character.isprintable():
            self._text = self._text[:self.cursor] + character + self._text[self.cursor:]
            self.cursor += len(character)
            self._changed()

    def _changed(self):
        if self.on_change:
            self.on_change(self._text)
        window = self.window()
        if window is not None and hasattr(window, "_uia_value_changed"):
            window._uia_value_changed(self)


class CheckBox(Widget):
    focusable = True

    def __init__(self, text="", checked=False, on_change=None):
        super().__init__()
        self.text = text
        self.checked = bool(checked)
        self.on_change = on_change

    def size_hint(self):
        return (max(120, measure_text(self.text, 2) + 34), 26)

    def paint(self, canvas):
        theme = self.theme()
        box = Rect(self.rect.x, self.rect.y + 3, 18, 18)
        canvas.rounded_rect(box, 4, theme.surface)
        canvas.draw_rect(box, theme.focus if self.focused else theme.border, 1)
        if self.checked:
            canvas.fill_rect(Rect(box.x + 4, box.y + 4, 10, 10), theme.accent)
        draw_text(canvas, self.text, box.right + 8, self.rect.y + 6,
                  theme.text, 2)

    def toggle(self):
        self.checked = not self.checked
        if self.on_change:
            self.on_change(self.checked)

    def mouse_up(self, x, y, button="left"):
        self.toggle()

    def key_down(self, key, modifiers=0):
        if key == VK_SPACE:
            self.toggle()


class Slider(Widget):
    focusable = True

    def __init__(self, minimum=0, maximum=100, value=0, on_change=None):
        super().__init__()
        self.minimum = int(minimum)
        self.maximum = int(maximum)
        self._value = int(value)
        self.on_change = on_change
        self.dragging = False

    def size_hint(self):
        return (220, 30)

    def value(self):
        return self._value

    def set_value(self, value):
        value = max(self.minimum, min(self.maximum, int(value)))
        if value != self._value:
            self._value = value
            if self.on_change:
                self.on_change(value)

    def _fraction(self):
        span = self.maximum - self.minimum
        return (self._value - self.minimum) / span if span else 0.0

    def paint(self, canvas):
        theme = self.theme()
        y = self.rect.y + self.rect.h / 2
        canvas.fill_rect(Rect(self.rect.x, y - 3, self.rect.w, 6),
                         theme.surface_alt)
        x = self.rect.x + self.rect.w * self._fraction()
        canvas.fill_rect(Rect(self.rect.x, y - 3, x - self.rect.x, 6),
                         theme.accent)
        canvas.fill_circle(x, y, 8, theme.accent)
        if self.focused:
            canvas.fill_circle(x, y, 10, theme.focus.with_alpha(90))

    def _set_from_x(self, x):
        fraction = max(0.0, min(1.0, (x - self.rect.x) / max(1, self.rect.w)))
        self.set_value(self.minimum + fraction * (self.maximum - self.minimum))

    def mouse_down(self, x, y, button="left"):
        self.dragging = True
        self._set_from_x(x)

    def mouse_move(self, x, y):
        if self.dragging:
            self._set_from_x(x)

    def mouse_up(self, x, y, button="left"):
        self.dragging = False

    def key_down(self, key, modifiers=0):
        if key == VK_LEFT:
            self.set_value(self._value - 1)
        elif key == VK_RIGHT:
            self.set_value(self._value + 1)


class ComboBox(Widget):
    focusable = True

    def __init__(self, items=None, current=0, on_change=None):
        super().__init__()
        self.items = list(items or [])
        self.current_index = max(0, min(len(self.items) - 1, int(current)))
        self.on_change = on_change

    def size_hint(self):
        return (200, self.theme().control_height)

    def current_text(self):
        return self.items[self.current_index] if self.items else ""

    def set_current_index(self, index):
        if not self.items:
            return
        index = max(0, min(len(self.items) - 1, int(index)))
        if index != self.current_index:
            self.current_index = index
            if self.on_change:
                self.on_change(self.current_text())

    def paint(self, canvas):
        theme = self.theme()
        canvas.rounded_rect(self.rect, theme.radius, theme.surface)
        canvas.draw_rect(self.rect, theme.focus if self.focused else theme.border, 1)
        draw_text(canvas, self.current_text(), self.rect.x + 8,
                  self.rect.y + 9, theme.text, 2)
        x = self.rect.right - 18
        y = self.rect.y + self.rect.h // 2
        canvas.line(x - 4, y - 2, x, y + 2, theme.muted, 2)
        canvas.line(x, y + 2, x + 4, y - 2, theme.muted, 2)

    def open_popup(self):
        window = self.window()
        if window is None or not self.items:
            return
        popup = ListPopup(self, self.items, self.current_index)
        width = self.rect.w
        height = min(window.canvas.height - 20, len(self.items) * 24 + 8)
        x = max(4, min(self.rect.x, window.canvas.width - width - 4))
        y = min(self.rect.bottom + 2, window.canvas.height - height - 4)
        popup.arrange(Rect(x, y, width, height))
        window.set_overlay(popup)

    def mouse_up(self, x, y, button="left"):
        self.open_popup()

    def key_down(self, key, modifiers=0):
        if key in (VK_UP, VK_LEFT):
            self.set_current_index(self.current_index - 1)
        elif key in (VK_DOWN, VK_RIGHT):
            self.set_current_index(self.current_index + 1)


class ListPopup(Widget):
    def __init__(self, combo, items, current=0):
        super().__init__()
        self.combo = combo
        self.items = list(items)
        self.current = current
        self.hover = current

    def paint(self, canvas):
        theme = self.theme()
        canvas.rounded_rect(self.rect, theme.radius, theme.surface)
        canvas.draw_rect(self.rect, theme.border, 1)
        for index, item in enumerate(self.items):
            row = Rect(self.rect.x + 4, self.rect.y + 4 + index * 24,
                       self.rect.w - 8, 24)
            if index == self.hover:
                canvas.rounded_rect(row, 4, theme.accent.with_alpha(70))
            draw_text(canvas, str(item), row.x + 6, row.y + 5,
                      theme.text, 2)

    def mouse_move(self, x, y):
        index = int((y - self.rect.y - 4) // 24)
        self.hover = max(0, min(len(self.items) - 1, index))

    def mouse_up(self, x, y, button="left"):
        index = max(0, min(len(self.items) - 1,
                           int((y - self.rect.y - 4) // 24)))
        self.combo.set_current_index(index)
        window = self.window()
        if window is not None:
            window.close_overlay()


class ProgressBar(Widget):
    def __init__(self, value=0, maximum=100):
        super().__init__()
        self.maximum = max(1, int(maximum))
        self._value = max(0, min(self.maximum, int(value)))

    def size_hint(self):
        return (200, 10)

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = max(0, min(self.maximum, int(value)))
        return self

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface_alt)
        width = int(self.rect.w * self._value / self.maximum)
        if width > 0:
            canvas.fill_rect(Rect(self.rect.x, self.rect.y, width,
                                  self.rect.h), theme.accent)


class ScrollBar(Widget):
    def __init__(self, orientation="vertical", maximum=100, page=100, value=0,
                 on_change=None):
        super().__init__()
        self.orientation = orientation
        self.maximum = max(1, int(maximum))
        self.page = max(1, int(page))
        self.value = int(value)
        self.on_change = on_change
        self.dragging = False
        self._drag_offset = 0

    def size_hint(self):
        return (14, 100) if self.orientation == "vertical" else (100, 14)

    def _thumb(self):
        if self.orientation == "vertical":
            track = self.rect.h
            size = max(20, track * self.page / max(self.maximum, self.page))
            travel = max(1, track - size)
            pos = self.rect.y + travel * self.value / self.maximum
            return Rect(self.rect.x + 2, pos, self.rect.w - 4, size)
        track = self.rect.w
        size = max(20, track * self.page / max(self.maximum, self.page))
        travel = max(1, track - size)
        pos = self.rect.x + travel * self.value / self.maximum
        return Rect(pos, self.rect.y + 2, size, self.rect.h - 4)

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface_alt)
        canvas.rounded_rect(self._thumb(), 5,
                            theme.accent if self.hovered or self.dragging
                            else theme.muted)

    def set_value(self, value):
        value = max(0, min(self.maximum, int(value)))
        if value != self.value:
            self.value = value
            if self.on_change:
                self.on_change(value)

    def mouse_down(self, x, y, button="left"):
        thumb = self._thumb()
        if thumb.contains(x, y):
            self.dragging = True
            self._drag_offset = y - thumb.y if self.orientation == "vertical" \
                else x - thumb.x
        else:
            self._jump(x, y)

    def _jump(self, x, y):
        if self.orientation == "vertical":
            fraction = (y - self.rect.y - 10) / max(1, self.rect.h - 20)
        else:
            fraction = (x - self.rect.x - 10) / max(1, self.rect.w - 20)
        self.set_value(fraction * self.maximum)

    def mouse_move(self, x, y):
        self.hovered = self.rect.contains(x, y)
        if not self.dragging:
            return
        thumb = self._thumb()
        if self.orientation == "vertical":
            track = max(1, self.rect.h - thumb.h)
            pos = y - self.rect.y - self._drag_offset
        else:
            track = max(1, self.rect.w - thumb.w)
            pos = x - self.rect.x - self._drag_offset
        self.set_value(max(0, min(1, pos / track)) * self.maximum)

    def mouse_up(self, x, y, button="left"):
        self.dragging = False


class ScrollArea(Widget):
    focusable = True

    def __init__(self, content=None, content_height=0):
        super().__init__()
        self.content = content or Panel()
        self.content.parent = self
        self.content_height = int(content_height)
        self.scroll_y = 0
        self.scrollbar = ScrollBar("vertical", on_change=self._scroll_to)
        self.scrollbar.parent = self

    def set_content(self, content, content_height=None):
        self.content = content
        content.parent = self
        if content_height is not None:
            self.content_height = int(content_height)
        return self

    def size_hint(self):
        return (300, 220)

    def arrange(self, rect):
        self.rect = rect
        height = max(rect.h, self.content_height or self.content.size_hint()[1])
        self.content_height = height
        viewport = Rect(rect.x, rect.y, max(1, rect.w - 14), rect.h)
        self.content.arrange(Rect(viewport.x, viewport.y - self.scroll_y,
                                  viewport.w, height))
        self.scrollbar.arrange(Rect(rect.right - 14, rect.y, 14, rect.h))
        self.scrollbar.maximum = max(0, height - rect.h)
        self.scrollbar.page = rect.h

    def _scroll_to(self, value):
        self.scroll_y = int(value)
        self.arrange(self.rect)

    def paint(self, canvas):
        canvas.push_clip(self.rect)
        try:
            self.content.paint(canvas)
        finally:
            canvas.pop_clip()
        self.scrollbar.paint(canvas)

    def wheel(self, delta):
        self.scrollbar.set_value(self.scroll_y - delta // 120 * 24)

    def key_down(self, key, modifiers=0):
        if key == VK_DOWN:
            self.wheel(-120)
        elif key == VK_UP:
            self.wheel(120)


class MenuAction:
    def __init__(self, label, callback=None, shortcut=""):
        self.label = label
        self.callback = callback
        self.shortcut = shortcut


class Menu:
    def __init__(self, label):
        self.label = label
        self.actions = []
        self.menus = []

    def add(self, label, callback=None, shortcut=""):
        action = MenuAction(label, callback, shortcut)
        self.actions.append(action)
        return action

    def add_menu(self, label):
        submenu = Menu(label)
        self.menus.append(submenu)
        return submenu

    def entries(self):
        return list(self.actions) + list(self.menus)


class MenuPopup(Widget):
    def __init__(self, menu):
        super().__init__()
        self.menu = menu
        self.hover = -1

    def entries(self):
        return self.menu.entries()

    def paint(self, canvas):
        theme = self.theme()
        canvas.rounded_rect(self.rect, theme.radius, theme.surface)
        canvas.draw_rect(self.rect, theme.border, 1)
        for index, entry in enumerate(self.entries()):
            row = Rect(self.rect.x + 4, self.rect.y + 4 + index * 26,
                       self.rect.w - 8, 26)
            if index == self.hover:
                canvas.rounded_rect(row, 4, theme.accent.with_alpha(70))
            label = entry.label
            draw_text(canvas, label, row.x + 6, row.y + 6, theme.text, 2)
            if isinstance(entry, Menu):
                draw_text(canvas, "›", row.right - 16, row.y + 5,
                          theme.muted, 2)
            elif entry.shortcut:
                width = measure_text(entry.shortcut, 1)
                draw_text(canvas, entry.shortcut, row.right - width - 6,
                          row.y + 7, theme.muted, 1)

    def mouse_move(self, x, y):
        index = int((y - self.rect.y - 4) // 26)
        self.hover = max(0, min(len(self.entries()) - 1, index))

    def mouse_up(self, x, y, button="left"):
        entries = self.entries()
        index = max(0, min(len(entries) - 1,
                           int((y - self.rect.y - 4) // 26)))
        entry = entries[index]
        window = self.window()
        if isinstance(entry, Menu):
            popup = MenuPopup(entry)
            width = max(170, max((measure_text(item.label, 2)
                                  for item in entry.entries()), default=0) + 40)
            height = len(entry.entries()) * 26 + 8
            popup.arrange(Rect(self.rect.right, self.rect.y + index * 26,
                               width, height))
            if window is not None:
                window.set_overlay(popup)
            return
        if window is not None:
            window.close_overlay()
        if entry.callback:
            entry.callback()


class ContextMenu(MenuPopup):
    def show_at(self, window, x, y):
        width = max(160, max((measure_text(action.label, 2)
                              for action in self.menu.actions), default=0) + 40)
        height = len(self.menu.actions) * 26 + 8
        self.arrange(Rect(x, y, width, height))
        window.set_overlay(self)


class MenuBar(Widget):
    def __init__(self, menus=None):
        super().__init__()
        self.menus = list(menus or [])
        self.active = -1

    def size_hint(self):
        return (400, 30)

    def add_menu(self, label):
        menu = Menu(label)
        self.menus.append(menu)
        return menu

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface_alt)
        x = self.rect.x + 6
        for index, menu in enumerate(self.menus):
            width = measure_text(menu.label, 2) + 16
            if index == self.active:
                canvas.fill_rect(Rect(x, self.rect.y, width, self.rect.h),
                                 theme.accent.with_alpha(70))
            draw_text(canvas, menu.label, x + 8, self.rect.y + 8,
                      theme.text, 2)
            menu._rect = Rect(x, self.rect.y, width, self.rect.h)
            x += width

    def mouse_up(self, x, y, button="left"):
        for index, menu in enumerate(self.menus):
            rect = getattr(menu, "_rect", None)
            if rect and rect.contains(x, y):
                self.active = index
                self.open_menu(menu)
                return

    def open_menu(self, menu):
        window = self.window()
        if window is None:
            return
        popup = MenuPopup(menu)
        width = max(180, max(measure_text(action.label, 2) for action in menu.actions) + 60)
        height = len(menu.actions) * 26 + 8
        popup.arrange(Rect(menu._rect.x, self.rect.bottom, width, height))
        window.set_overlay(popup)


class TableView(Widget):
    focusable = True

    def __init__(self, columns=None, rows=None, on_select=None):
        super().__init__()
        self.columns = list(columns or ["Spalte"])
        self.rows = [list(row) for row in (rows or [])]
        self.selected = -1
        self.scroll = 0
        self.on_select = on_select
        self.row_height = 26
        self.header_height = 28
        self.selected_col = 0
        self.editor = None
        self.column_widths = []
        self.sort_column = -1
        self.sort_descending = False
        self.multi_select = False
        self.selected_rows = set()
        self.on_select_many = None
        self._resizing = -1
        self._resize_x = 0

    def size_hint(self):
        return (360, 220)

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface)
        canvas.fill_rect(Rect(self.rect.x, self.rect.y, self.rect.w,
                              self.header_height), theme.surface_alt)
        widths = self._widths()
        x = self.rect.x + 4
        for index, column in enumerate(self.columns):
            label = str(column)
            if index == self.sort_column:
                label += " ▼" if self.sort_descending else " ▲"
            draw_text(canvas, label, x + 4, self.rect.y + 7,
                      theme.muted, 2)
            x += widths[index]
        canvas.line(self.rect.x, self.rect.y + self.header_height,
                    self.rect.right, self.rect.y + self.header_height,
                    theme.border, 1)
        visible = int((self.rect.h - self.header_height) // self.row_height)
        for visible_index in range(min(visible, len(self.rows) - self.scroll)):
            index = self.scroll + visible_index
            y = self.rect.y + self.header_height + visible_index * self.row_height
            if index == self.selected or index in self.selected_rows:
                canvas.fill_rect(Rect(self.rect.x, y, self.rect.w,
                                      self.row_height), theme.accent.with_alpha(60))
            x = self.rect.x + 4
            for column, value in enumerate(self.rows[index]):
                draw_text(canvas, str(value), x + 4, y + 5, theme.text, 2)
                x += widths[column] if column < len(widths) else 0
        for child in self.children:
            child.paint(canvas)

    def _widths(self):
        count = max(1, len(self.columns))
        if len(self.column_widths) != count:
            self.column_widths = [max(60, self.rect.w // count)] * count
        return self.column_widths

    def _sort(self, column):
        if not (0 <= column < len(self.columns)):
            return
        if self.sort_column == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = column
            self.sort_descending = False
        self.rows.sort(key=lambda row: (str(row[column])
                                        if column < len(row) else ""),
                       reverse=self.sort_descending)
        self.selected = -1

    def _header_column(self, x):
        offset = x - self.rect.x - 4
        for index, width in enumerate(self._widths()):
            if offset < width:
                return index, offset
            offset -= width
        return len(self.columns) - 1, offset

    def mouse_down(self, x, y, button="left"):
        self.commit_edit()
        if y >= self.rect.y + self.header_height:
            return
        column, offset = self._header_column(x)
        width = self._widths()[column]
        if abs(offset - width) <= 4:
            self._resizing = column
            self._resize_x = x
        else:
            self._sort(column)

    def mouse_move(self, x, y):
        if self._resizing >= 0:
            widths = self._widths()
            widths[self._resizing] = max(40, widths[self._resizing] +
                                         (x - self._resize_x))
            self._resize_x = x

    def mouse_up(self, x, y, button="left"):
        if self._resizing >= 0:
            self._resizing = -1
            return
        if y < self.rect.y + self.header_height:
            return
        index = self.scroll + int((y - self.rect.y - self.header_height) //
                                  self.row_height)
        if 0 <= index < len(self.rows):
            if self.multi_select:
                if index in self.selected_rows:
                    self.selected_rows.remove(index)
                else:
                    self.selected_rows.add(index)
                if self.on_select_many:
                    self.on_select_many(sorted(self.selected_rows))
            else:
                self.selected_rows = {index}
            self.selected = index
            widths = self._widths()
            offset = x - self.rect.x - 4
            column = 0
            for column_index, width in enumerate(widths):
                if offset < width:
                    column = column_index
                    break
                offset -= width
            self.selected_col = column
            if self.on_select:
                self.on_select(index, self.rows[index])

    def begin_edit(self):
        if self.selected < 0 or self.selected >= len(self.rows):
            return None
        row = self.rows[self.selected]
        if self.selected_col >= len(row):
            return None
        from .widgets import LineEdit
        self.editor = LineEdit(str(row[self.selected_col]))
        self.editor.on_enter = self.commit_edit
        self.editor.arrange(Rect(self.rect.x + 4, self.rect.y +
                                 self.header_height +
                                 (self.selected - self.scroll) * self.row_height,
                                 max(80, self.rect.w - 8), self.row_height))
        self.add(self.editor)
        return self.editor

    def commit_edit(self):
        if self.editor is not None and 0 <= self.selected < len(self.rows):
            row = self.rows[self.selected]
            while len(row) <= self.selected_col:
                row.append("")
            row[self.selected_col] = self.editor.text()
            self.children.remove(self.editor)
            self.editor = None
            window = self.window()
            if window is not None and hasattr(window, "set_focus"):
                window.set_focus(self)
            return True
        return False

    def key_down(self, key, modifiers=0):
        if key == VK_RETURN:
            self.begin_edit()
            return
        if key == VK_DOWN:
            self.selected = min(len(self.rows) - 1, self.selected + 1)
        elif key == VK_UP:
            self.selected = max(0, self.selected - 1)


class TreeItem:
    def __init__(self, label, children=None, icon=None, data=None):
        self.label = label
        self.children = list(children or [])
        self.icon = icon
        self.data = data
        self.expanded = True


class TreeView(Widget):
    focusable = True

    def __init__(self, items=None, on_select=None):
        super().__init__()
        self.items = list(items or [])
        self.selected = None
        self.on_select = on_select
        self.on_move = None
        self.draggable = True
        self._drag_item = None
        self._drag_start = None
        self._dragging = False

    def size_hint(self):
        return (300, 240)

    def _flatten(self, items, depth=0):
        result = []
        for item in items:
            result.append((item, depth))
            if item.expanded and item.children:
                result.extend(self._flatten(item.children, depth + 1))
        return result

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface)
        y = self.rect.y + 4
        for item, depth in self._flatten(self.items):
            row = Rect(self.rect.x, y, self.rect.w, 24)
            if item is self.selected:
                canvas.fill_rect(row, theme.accent.with_alpha(60))
            x = self.rect.x + 8 + depth * 12
            if item.children:
                draw_text(canvas, "▾" if item.expanded else "▸", x, y + 4,
                          theme.muted, 2)
            if getattr(item, "icon", None) is not None:
                icon = item.icon
                if isinstance(icon, Color):
                    canvas.fill_rect(Rect(x + 16, y + 7, 10, 10), icon)
                else:
                    draw_text(canvas, str(icon), x + 16, y + 5, theme.text, 2)
                text_x = x + 34
            else:
                text_x = x + 16
            draw_text(canvas, item.label, text_x, y + 5, theme.text, 2)
            y += 24

    def _item_at(self, y):
        index = int((y - self.rect.y - 4) // 24)
        flat = self._flatten(self.items)
        if 0 <= index < len(flat):
            return flat[index]
        return None, 0

    def mouse_down(self, x, y, button="left"):
        item, depth = self._item_at(y)
        self._drag_item = item
        self._drag_start = (x, y)
        self._dragging = False

    def mouse_move(self, x, y):
        if self._drag_item is None or self._drag_start is None:
            return
        if abs(x - self._drag_start[0]) + abs(y - self._drag_start[1]) > 5:
            self._dragging = True

    def _remove_item(self, item, items=None):
        items = self.items if items is None else items
        if item in items:
            items.remove(item)
            return True
        for candidate in items:
            if self._remove_item(item, candidate.children):
                return True
        return False

    def _contains(self, item, other):
        if item is other:
            return True
        return any(self._contains(child, other) for child in item.children)

    def mouse_up(self, x, y, button="left"):
        item, depth = self._item_at(y)
        if self._dragging and self._drag_item is not None and item is not None:
            source = self._drag_item
            if source is not item and not self._contains(source, item):
                self._remove_item(source)
                item.children.append(source)
                item.expanded = True
                self.selected = source
                if self.on_move:
                    self.on_move(source, item)
                self._dragging = False
                self._drag_item = None
                return
        self._dragging = False
        self._drag_item = None
        if item is None:
            return
        if item.children and x < self.rect.x + 24 + depth * 12:
            item.expanded = not item.expanded
            return
        self.selected = item
        if self.on_select:
            self.on_select(self.selected)

    def expand_all(self):
        for item in self._all_items(self.items):
            item.expanded = True

    def collapse_all(self):
        for item in self._all_items(self.items):
            item.expanded = False

    def _all_items(self, items):
        for item in items:
            yield item
            yield from self._all_items(item.children)

    def key_down(self, key, modifiers=0):
        flat = self._flatten(self.items)
        if not flat:
            return
        labels = [item for item, _ in flat]
        index = labels.index(self.selected) if self.selected in labels else 0
        if key == VK_DOWN:
            index = min(len(labels) - 1, index + 1)
        elif key == VK_UP:
            index = max(0, index - 1)
        elif key == VK_RIGHT and self.selected is not None:
            self.selected.expanded = True
            return
        elif key == VK_LEFT and self.selected is not None:
            self.selected.expanded = False
            return
        self.selected = labels[index]


class BoxLayout:
    def __init__(self, orientation="vertical", spacing=8, padding=12):
        self.orientation = orientation
        self.spacing = spacing
        self.padding = padding
        self.items = []

    def add(self, widget, stretch=0):
        self.items.append((widget, stretch))
        return widget

    def arrange(self, root, rect):
        count = len(self.items)
        if not count:
            return
        inner = Rect(rect.x + self.padding, rect.y + self.padding,
                     max(1, rect.w - 2 * self.padding),
                     max(1, rect.h - 2 * self.padding))
        horizontal = self.orientation == "horizontal"
        main = inner.w if horizontal else inner.h
        main -= self.spacing * (count - 1)
        hints = []
        for widget, stretch in self.items:
            hint = widget.size_hint()
            hints.append(hint[0] if horizontal else hint[1])
        fixed = sum(hints)
        stretch_total = sum(stretch for _, stretch in self.items)
        extra = max(0, main - fixed)
        sizes = list(hints)
        if stretch_total and extra:
            for index, (_, stretch) in enumerate(self.items):
                sizes[index] += int(extra * stretch / stretch_total)
        pos = inner.x if horizontal else inner.y
        for index, (widget, _stretch) in enumerate(self.items):
            if horizontal:
                child = Rect(pos, inner.y, sizes[index], inner.h)
            else:
                child = Rect(inner.x, pos, inner.w, sizes[index])
            widget.arrange(child)
            pos += sizes[index] + self.spacing


class GridLayout:
    def __init__(self, columns=2, spacing=8, padding=12):
        self.columns = max(1, int(columns))
        self.spacing = spacing
        self.padding = padding
        self.items = []

    def add(self, widget, row=0, column=0, rowspan=1, colspan=1):
        self.items.append((widget, row, column, rowspan, colspan))
        return widget

    def arrange(self, root, rect):
        if not self.items:
            return
        rows = max(row + rowspan for _, row, _, rowspan, _ in self.items)
        widths = [0] * self.columns
        heights = [0] * rows
        for widget, row, column, rowspan, colspan in self.items:
            hint = widget.size_hint()
            for col in range(column, min(self.columns, column + colspan)):
                widths[col] = max(widths[col], hint[0] // max(1, colspan))
            heights[row] = max(heights[row], hint[1])
        total_w = sum(widths) + self.spacing * (self.columns - 1)
        total_h = sum(heights) + self.spacing * (rows - 1)
        inner = Rect(rect.x + self.padding, rect.y + self.padding,
                     max(1, rect.w - 2 * self.padding),
                     max(1, rect.h - 2 * self.padding))
        scale_w = inner.w / total_w if total_w else 1
        scale_h = inner.h / total_h if total_h else 1
        widths = [width * scale_w for width in widths]
        heights = [height * scale_h for height in heights]
        for widget, row, column, rowspan, colspan in self.items:
            x = inner.x + sum(widths[:column]) + self.spacing * column
            y = inner.y + sum(heights[:row]) + self.spacing * row
            w = sum(widths[column:column + colspan]) + self.spacing * (colspan - 1)
            h = sum(heights[row:row + rowspan]) + self.spacing * (rowspan - 1)
            widget.arrange(Rect(x, y, w, h))


class FormLayout:
    def __init__(self, spacing=8, padding=12, label_width=120):
        self.spacing = spacing
        self.padding = padding
        self.label_width = label_width
        self.rows = []

    def add(self, label, field):
        self.rows.append((label, field))
        return field

    def arrange(self, root, rect):
        if not self.rows:
            return
        height = (rect.h - 2 * self.padding - self.spacing *
                  (len(self.rows) - 1)) / len(self.rows)
        y = rect.y + self.padding
        for label, field in self.rows:
            label.arrange(Rect(rect.x + self.padding, y, self.label_width,
                               height))
            field.arrange(Rect(rect.x + self.padding + self.label_width,
                               y, rect.w - 2 * self.padding -
                               self.label_width, height))
            y += height + self.spacing
