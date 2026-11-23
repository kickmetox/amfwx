"""Windows system tray icon."""

from __future__ import annotations

import ctypes
from ctypes import POINTER, byref, c_void_p, wintypes


NIM_ADD = 0
NIM_MODIFY = 1
NIM_DELETE = 2
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
IDI_APPLICATION = 32512
TPM_RETURNCMD = 0x0100
TPM_LEFTALIGN = 0x0000
MF_STRING = 0x00000000


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
        ("guidItem", ctypes.c_byte * 16),
        ("hBalloonIcon", wintypes.HICON),
    ]


shell32 = ctypes.WinDLL("shell32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)
shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD,
                                      POINTER(NOTIFYICONDATAW)]
shell32.Shell_NotifyIconW.restype = wintypes.BOOL
user32.LoadIconW.argtypes = [wintypes.HINSTANCE, ctypes.c_void_p]
user32.LoadIconW.restype = wintypes.HICON
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT,
                               wintypes.UINT, wintypes.LPCWSTR]
user32.TrackPopupMenu.argtypes = [wintypes.HMENU, wintypes.UINT,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  wintypes.HWND, ctypes.c_void_p]
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.GetCursorPos.argtypes = [ctypes.c_void_p]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]


class TrayIcon:
    def __init__(self, window, tooltip="AMFWX", icon_id=1):
        self.window = window
        self.tooltip = str(tooltip)
        self.icon_id = int(icon_id)
        self.icon = None
        self.visible = False

    def _data(self):
        data = NOTIFYICONDATAW()
        data.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        data.hWnd = self.window.hwnd
        data.uID = self.icon_id
        data.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        data.uCallbackMessage = 0x0400 + 100
        if self.icon is None:
            try:
                from .icons import load_icon
                self.icon = load_icon()
            except Exception:
                self.icon = None
        data.hIcon = self.icon or user32.LoadIconW(None, IDI_APPLICATION)
        data.szTip = self.tooltip[:127]
        return data

    def add(self):
        try:
            from .icons import load_icon
            self.icon = load_icon()
        except Exception:
            self.icon = None
        if self.icon is None:
            self.icon = user32.LoadIconW(None, IDI_APPLICATION)
        data = self._data()
        ok = shell32.Shell_NotifyIconW(NIM_ADD, byref(data))
        self.visible = bool(ok)
        return self.visible

    def set_tooltip(self, text):
        self.tooltip = str(text)
        data = self._data()
        shell32.Shell_NotifyIconW(NIM_MODIFY, byref(data))
        return self

    def remove(self):
        data = self._data()
        shell32.Shell_NotifyIconW(NIM_DELETE, byref(data))
        self.visible = False
        return self

    def show_menu(self, items):
        menu = user32.CreatePopupMenu()
        ids = {}
        for offset, (label, callback) in enumerate(items, 1):
            ids[offset] = callback
            user32.AppendMenuW(menu, MF_STRING, offset, str(label))
        point = wintypes.POINT()
        user32.GetCursorPos(byref(point))
        user32.SetForegroundWindow(self.window.hwnd)
        choice = user32.TrackPopupMenu(menu, TPM_RETURNCMD | TPM_LEFTALIGN,
                                       point.x, point.y, 0, self.window.hwnd,
                                       None)
        user32.DestroyMenu(menu)
        callback = ids.get(int(choice))
        if callback is not None:
            callback()
        return callback is not None
