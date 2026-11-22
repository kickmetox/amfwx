"""AMFWX Unicode clipboard (text)."""

from __future__ import annotations

import ctypes
import time
from ctypes import wintypes

user32 = ctypes.WinDLL("user32")
shell32 = ctypes.WinDLL("shell32")
kernel32 = ctypes.WinDLL("kernel32")
CF_UNICODETEXT = 13
CF_HDROP = 15
CF_DIB = 8
user32.RegisterClipboardFormatW.argtypes = [ctypes.c_wchar_p]
user32.RegisterClipboardFormatW.restype = ctypes.c_uint
CF_HTML = user32.RegisterClipboardFormatW("HTML Format")
shell32.DragQueryFileW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_uint]
shell32.DragQueryFileW.restype = ctypes.c_uint
GMEM_MOVEABLE = 0x0042


def _open_clipboard(retries=8):
    for _ in range(retries):
        if user32.OpenClipboard(None):
            return True
        time.sleep(0.01)
    return False


user32.OpenClipboard.argtypes = [ctypes.c_void_p]
user32.OpenClipboard.restype = ctypes.c_int
user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
user32.SetClipboardData.restype = ctypes.c_void_p
user32.GetClipboardData.argtypes = [ctypes.c_uint]
user32.GetClipboardData.restype = ctypes.c_void_p
kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]


def set_text(text):
    data = (str(text) + "\0").encode("utf-16-le")
    if not _open_clipboard():
        return False
    try:
        user32.EmptyClipboard()
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not handle:
            return False
        pointer = kernel32.GlobalLock(handle)
        ctypes.memmove(pointer, data, len(data))
        kernel32.GlobalUnlock(handle)
        user32.SetClipboardData(CF_UNICODETEXT, handle)
        return True
    finally:
        user32.CloseClipboard()


def get_text():
    if not _open_clipboard():
        return ""
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        pointer = kernel32.GlobalLock(handle)
        try:
            return ctypes.wstring_at(pointer) if pointer else ""
        finally:
            if pointer:
                kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()


def set_html(fragment, plain_text=None):
    fragment = str(fragment)
    html = ("<html><body><!--StartFragment-->" + fragment +
            "<!--EndFragment--></body></html>")
    header = ("Version:0.9\r\nStartHTML:{start:010d}\r\n"
              "EndHTML:{end:010d}\r\nStartFragment:{frag_start:010d}\r\n"
              "EndFragment:{frag_end:010d}\r\n")
    # Fixed-width placeholders keep offsets stable.
    placeholder = header.format(start=0, end=0, frag_start=0, frag_end=0)
    start = len(placeholder)
    frag_start = start + html.index("<!--StartFragment-->") + len("<!--StartFragment-->")
    frag_end = frag_start + len(fragment)
    end = start + len(html)
    payload = header.format(start=start, end=end, frag_start=frag_start,
                            frag_end=frag_end) + html
    data = (payload + "\0").encode("utf-8")
    if plain_text is not None:
        set_text(plain_text)
    if not _open_clipboard():
        return False
    try:
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        pointer = kernel32.GlobalLock(handle)
        ctypes.memmove(pointer, data, len(data))
        kernel32.GlobalUnlock(handle)
        user32.SetClipboardData(CF_HTML, handle)
        return True
    finally:
        user32.CloseClipboard()


def get_html():
    if not _open_clipboard():
        return ""
    try:
        handle = user32.GetClipboardData(CF_HTML)
        if not handle:
            return ""
        pointer = kernel32.GlobalLock(handle)
        try:
            raw = ctypes.string_at(pointer).decode("utf-8", "replace")
        finally:
            if pointer:
                kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()
    start = raw.find("<!--StartFragment-->")
    end = raw.find("<!--EndFragment-->")
    if start >= 0 and end > start:
        return raw[start + len("<!--StartFragment-->"):end]
    return raw


class DROPFILES(ctypes.Structure):
    _fields_ = [("pFiles", ctypes.c_uint), ("pt", wintypes.POINT),
                ("fNC", wintypes.BOOL), ("fWide", wintypes.BOOL)]


def set_files(paths):
    text = "\0".join(str(path) for path in paths) + "\0\0"
    data = text.encode("utf-16-le")
    header = ctypes.sizeof(DROPFILES)
    size = header + len(data)
    if not _open_clipboard():
        return False
    try:
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
        pointer = kernel32.GlobalLock(handle)
        info = DROPFILES()
        info.pFiles = header
        info.fWide = True
        ctypes.memmove(pointer, ctypes.byref(info), header)
        ctypes.memmove(pointer + header, data, len(data))
        kernel32.GlobalUnlock(handle)
        user32.SetClipboardData(CF_HDROP, handle)
        return True
    finally:
        user32.CloseClipboard()


def get_files():
    if not _open_clipboard():
        return []
    try:
        handle = user32.GetClipboardData(CF_HDROP)
        if not handle:
            return []
        count = shell32.DragQueryFileW(ctypes.c_void_p(handle), 0xFFFFFFFF,
                                      None, 0)
        paths = []
        for index in range(count):
            buffer = ctypes.create_unicode_buffer(2048)
            shell32.DragQueryFileW(ctypes.c_void_p(handle), index, buffer, 2048)
            paths.append(buffer.value)
        return paths
    finally:
        user32.CloseClipboard()


def set_image(canvas):
    width, height = canvas.width, canvas.height
    header = bytearray(40)
    header[0:4] = (40).to_bytes(4, "little")
    header[4:8] = width.to_bytes(4, "little", signed=True)
    header[8:12] = height.to_bytes(4, "little", signed=True)
    header[12:14] = (1).to_bytes(2, "little")
    header[14:16] = (32).to_bytes(2, "little")
    header[20:24] = (width * height * 4).to_bytes(4, "little")
    pixels = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            color = canvas.pixel(x, y)
            pixels += bytes((color.b, color.g, color.r, 255))
    data = bytes(header) + bytes(pixels)
    if not _open_clipboard():
        return False
    try:
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        pointer = kernel32.GlobalLock(handle)
        ctypes.memmove(pointer, data, len(data))
        kernel32.GlobalUnlock(handle)
        user32.SetClipboardData(CF_DIB, handle)
        return True
    finally:
        user32.CloseClipboard()


def get_image():
    from .canvas import Canvas, Color
    if not _open_clipboard():
        return None
    try:
        handle = user32.GetClipboardData(CF_DIB)
        if not handle:
            return None
        pointer = kernel32.GlobalLock(handle)
        try:
            import struct
            header = ctypes.string_at(pointer, 40)
            size, width, height, planes, bits = struct.unpack("<IiiHH", header[:16])
            if bits not in (24, 32):
                return None
            stride = ((width * bits + 31) // 32) * 4
            raw = ctypes.string_at(pointer + 40, stride * abs(height))
        finally:
            if pointer:
                kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()
    canvas = Canvas(width, abs(height))
    for y in range(abs(height)):
        source_y = abs(height) - 1 - y if height > 0 else y
        row = raw[source_y * stride:(source_y + 1) * stride]
        for x in range(width):
            offset = x * (bits // 8)
            b, g, r = row[offset:offset + 3]
            canvas.set_pixel(x, y, Color(r, g, b))
    return canvas
