"""libwebp binding for AMFWX (BGRA decode/encode)."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
from ctypes import c_char_p, c_float, c_int, c_size_t, c_void_p, byref, POINTER

from .canvas import Canvas, Color

_DLL = None


def _library():
    global _DLL
    if _DLL is not None:
        return _DLL
    path = os.path.join(os.path.dirname(__file__), "bin", "libwebp.dll")
    library = ctypes.WinDLL(path)
    library.WebPGetInfo.argtypes = [c_void_p, c_size_t,
                                    POINTER(c_int), POINTER(c_int)]
    library.WebPGetInfo.restype = c_int
    library.WebPDecodeBGRA.argtypes = [c_void_p, c_size_t,
                                       POINTER(c_int), POINTER(c_int)]
    library.WebPDecodeBGRA.restype = c_void_p
    library.WebPFree.argtypes = [c_void_p]
    library.WebPEncodeBGRA.argtypes = [c_void_p, c_int, c_int, c_int, c_float,
                                       POINTER(c_void_p)]
    library.WebPEncodeBGRA.restype = c_size_t
    _DLL = library
    return library


def probe_webp():
    try:
        _library()
        return True
    except OSError:
        return False


def decode_webp(data):
    library = _library()
    raw = ctypes.create_string_buffer(bytes(data), len(data))
    width = c_int()
    height = c_int()
    if not library.WebPGetInfo(raw, len(data), byref(width), byref(height)):
        raise ValueError("ungültiges WebP")
    pointer = library.WebPDecodeBGRA(raw, len(data), byref(width), byref(height))
    if not pointer:
        raise ValueError("WebP-Dekodierung fehlgeschlagen")
    try:
        pixels = ctypes.string_at(pointer, width.value * height.value * 4)
    finally:
        library.WebPFree(pointer)
    return width.value, height.value, pixels


def encode_webp(canvas, quality=90):
    library = _library()
    data = (ctypes.c_ubyte * len(canvas.data)).from_buffer(canvas.data)
    output = c_void_p()
    size = library.WebPEncodeBGRA(data, canvas.width, canvas.height,
                                  canvas.width * 4, float(quality),
                                  byref(output))
    if not size or not output.value:
        raise ValueError("WebP-Encoding fehlgeschlagen")
    try:
        return ctypes.string_at(output, size)
    finally:
        library.WebPFree(output)


Canvas.from_webp = classmethod(
    lambda cls, path: _canvas_from_bytes(Path(path).read_bytes()))


def _canvas_from_bytes(data):
    width, height, pixels = decode_webp(data)
    canvas = Canvas(width, height)
    canvas.data[:] = pixels
    return canvas

