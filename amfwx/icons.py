"""Runtime window/tray icon helpers."""

from __future__ import annotations

import ctypes
from pathlib import Path
from ctypes import wintypes

IMAGE_ICON = 1
LR_LOADFROMFILE = 0x0010
LR_DEFAULTSIZE = 0x0040
WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG = 1

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR,
                              wintypes.UINT, ctypes.c_int, ctypes.c_int,
                              wintypes.UINT]
user32.LoadImageW.restype = wintypes.HANDLE
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT,
                                wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = wintypes.LPARAM


def default_icon_path():
    package = Path(__file__).resolve().parent
    candidates = [package / "bin" / "AMFWX.ico",
                  package.parent / "assets" / "AMFWX.ico"]
    for path in candidates:
        if path.is_file():
            return path
    return None


def load_icon(path=None, size=0):
    path = Path(path) if path else default_icon_path()
    if path is None or not Path(path).is_file():
        return None
    handle = user32.LoadImageW(None, str(path), IMAGE_ICON, int(size),
                               int(size), LR_LOADFROMFILE | LR_DEFAULTSIZE)
    return handle or None


def set_window_icon(window, path=None):
    handle = load_icon(path)
    if not handle:
        return False
    user32.SendMessageW(window.hwnd, WM_SETICON, ICON_SMALL, handle)
    user32.SendMessageW(window.hwnd, WM_SETICON, ICON_BIG, handle)
    return True
