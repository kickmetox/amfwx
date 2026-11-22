"""AMFWX native file dialogs via comdlg32 (OS dialog, not a UI framework)."""

from __future__ import annotations

import ctypes
from ctypes import POINTER, byref, c_int, c_void_p, c_wchar_p, create_unicode_buffer
from ctypes import wintypes

comdlg32 = ctypes.WinDLL("comdlg32")
OFN_OVERWRITEPROMPT = 0x00000002
OFN_FILEMUSTEXIST = 0x00001000
OFN_PATHMUSTEXIST = 0x00000800
OFN_EXPLORER = 0x00080000


class OPENFILENAMEW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD), ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE), ("lpstrFilter", c_wchar_p),
        ("lpstrCustomFilter", c_wchar_p), ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD), ("lpstrFile", c_wchar_p),
        ("nMaxFile", wintypes.DWORD), ("lpstrFileTitle", c_wchar_p),
        ("nMaxFileTitle", wintypes.DWORD), ("lpstrInitialDir", c_wchar_p),
        ("lpstrTitle", c_wchar_p), ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD), ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", c_wchar_p), ("lCustData", wintypes.LPARAM),
        ("lpfnHook", c_void_p), ("lpTemplateName", c_wchar_p),
        ("pvReserved", c_void_p), ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]


comdlg32.GetOpenFileNameW.argtypes = [POINTER(OPENFILENAMEW)]
comdlg32.GetOpenFileNameW.restype = wintypes.BOOL
comdlg32.GetSaveFileNameW.argtypes = [POINTER(OPENFILENAMEW)]
comdlg32.GetSaveFileNameW.restype = wintypes.BOOL


def _filter(value):
    if not value:
        return "Alle Dateien (*.*)\0*.*\0\0"
    if isinstance(value, str):
        parts = value.split("|")
        value = [(parts[index], parts[index + 1])
                 for index in range(0, len(parts) - 1, 2)]
    chunks = []
    for label, pattern in value:
        chunks.append(f"{label} ({pattern})")
        chunks.append(pattern)
    return "\0".join(chunks) + "\0\0"


def open_file(parent=None, title="Datei öffnen", filters=None,
              initial_dir=""):
    buffer = create_unicode_buffer(2048)
    info = OPENFILENAMEW()
    info.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    info.hwndOwner = getattr(parent, "hwnd", None)
    info.lpstrFilter = _filter(filters)
    info.lpstrFile = ctypes.cast(buffer, c_wchar_p)
    info.nMaxFile = 2048
    info.lpstrTitle = title
    info.lpstrInitialDir = initial_dir
    info.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_EXPLORER
    if comdlg32.GetOpenFileNameW(byref(info)):
        return buffer.value
    return ""


def save_file(parent=None, title="Datei speichern", filters=None,
              default_name="", default_extension=""):
    buffer = create_unicode_buffer(default_name, 2048)
    info = OPENFILENAMEW()
    info.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    info.hwndOwner = getattr(parent, "hwnd", None)
    info.lpstrFilter = _filter(filters)
    info.lpstrFile = ctypes.cast(buffer, c_wchar_p)
    info.nMaxFile = 2048
    info.lpstrTitle = title
    info.lpstrDefExt = default_extension
    info.Flags = OFN_OVERWRITEPROMPT | OFN_PATHMUSTEXIST | OFN_EXPLORER
    if comdlg32.GetSaveFileNameW(byref(info)):
        return buffer.value
    return ""
