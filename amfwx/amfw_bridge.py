"""Optional bridge: host AMFWX widgets inside an AMFW window.

AMFW keeps the Win32 window/event loop. AMFWX only supplies its own widgets
and rasterizer; no second message loop is created.
"""

from __future__ import annotations

from amfw import Widget
from amfw.gui.image import Image

import ctypes
from ctypes import byref, c_int, c_void_p

from .canvas import Canvas, Color, Rect
from .theme import DARK


class _ThemeHost:
    def __init__(self, theme):
        self.theme = theme


class AmfwxView(Widget):
    """AMFW widget that renders an AMFWX widget tree into a bitmap."""

    def __init__(self, root, width=420, height=260, theme=None):
        super().__init__()
        self.root = root
        self.surface_width = int(width)
        self.surface_height = int(height)
        self.amfwx_theme = theme or DARK
        self.focus = None
        self.set_size_hint(width, height)
        self._image = None
        self.root.parent = _ThemeHost(self.amfwx_theme)

    def _arrange(self):
        self.root.arrange(Rect(0, 0, self.surface_width, self.surface_height))
        layout = getattr(self.root, "layout", None)
        if layout is not None:
            layout.arrange(self.root, self.root.rect)

    def _canvas(self):
        self._arrange()
        canvas = Canvas(self.surface_width, self.surface_height,
                        self.amfwx_theme.background)
        self.root.paint(canvas)
        return canvas

    def paint(self, painter):
        canvas = self._canvas()
        rgba = bytearray()
        for index in range(0, len(canvas.data), 4):
            b, g, r, a = canvas.data[index:index + 4]
            rgba.extend((r, g, b, a))
        self._image = Image.from_rgba(canvas.width, canvas.height, bytes(rgba))
        painter.draw_image_xy(0, 0, self._image)

    def size_hint(self):
        return (self.surface_width, self.surface_height)

    def _target(self, x, y):
        return self.root.hit_test(x, y)

    def mouse_press_event(self, event):
        target = self._target(event.x, event.y)
        if target is not None and target.focusable:
            if self.focus is not None:
                self.focus.set_focused(False)
            self.focus = target
            target.set_focused(True)
        if target is not None:
            target.mouse_down(event.x, event.y)
        self.update()

    def mouse_move_event(self, event):
        target = self._target(event.x, event.y)
        if target is not None:
            target.mouse_move(event.x, event.y)
        elif self.root is not None:
            self.root.mouse_move(event.x, event.y)
        self.update()

    def mouse_release_event(self, event):
        target = self._target(event.x, event.y)
        if target is not None:
            target.mouse_up(event.x, event.y)
        self.update()

    def key_press_event(self, event):
        if self.focus is not None:
            self.focus.key_down(event.key, event.modifiers)
            self.update()

    def key_char_event(self, event):
        if self.focus is not None:
            self.focus.char_input(event.text)
            self.update()


class AmfwxWindowHost:
    """Reverse bridge: embed a real AMFW Window as a native child."""

    def __init__(self, amfw_window):
        self.amfw_window = amfw_window
        self.host_hwnd = None

    def attach(self, amfwx_window):
        user32 = ctypes.WinDLL("user32")
        user32.SetParent.argtypes = [c_void_p, c_void_p]
        user32.SetParent.restype = c_void_p
        user32.GetWindowLongPtrW.argtypes = [c_void_p, c_int]
        user32.GetWindowLongPtrW.restype = ctypes.c_longlong
        user32.SetWindowLongPtrW.argtypes = [c_void_p, c_int, ctypes.c_longlong]
        user32.SetWindowLongPtrW.restype = ctypes.c_longlong
        user32.MoveWindow.argtypes = [c_void_p, c_int, c_int, c_int, c_int,
                                      c_int]
        self.host_hwnd = amfwx_window.hwnd
        user32.SetParent(self.amfw_window.hwnd, self.host_hwnd)
        style = user32.GetWindowLongPtrW(self.amfw_window.hwnd, -16)
        user32.SetWindowLongPtrW(self.amfw_window.hwnd, -16,
                                 style | 0x40000000 | 0x10000000)
        user32.MoveWindow(self.amfw_window.hwnd, 0, 0,
                          amfwx_window.width, amfwx_window.height, 1)
        return self

    def resize(self, x, y, width, height):
        if self.host_hwnd:
            ctypes.WinDLL("user32").MoveWindow(
                self.amfw_window.hwnd, int(x), int(y), int(width),
                int(height), 1)
        return self


