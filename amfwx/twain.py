"""TWAIN data-source enumeration for old and new scanners."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path


DG_CONTROL = 1
DAT_PARENT = 4
DAT_IDENTITY = 3
MSG_OPENDSM = 0x0301
MSG_CLOSEDSM = 0x0302
MSG_GETFIRST = 0x0004
MSG_GETNEXT = 0x0005


class TW_VERSION(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("MajorNum", wintypes.WORD),
                ("MinorNum", wintypes.WORD),
                ("Language", wintypes.WORD),
                ("Country", wintypes.WORD),
                ("Info", wintypes.WCHAR * 34)]


class TW_IDENTITY(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("Id", wintypes.ULONG),
                ("Version", TW_VERSION),
                ("ProtocolMajor", wintypes.WORD),
                ("ProtocolMinor", wintypes.WORD),
                ("SupportedGroups", wintypes.ULONG),
                ("Manufacturer", wintypes.WCHAR * 34),
                ("ProductFamily", wintypes.WCHAR * 34),
                ("ProductName", wintypes.WCHAR * 34)]


class TwainSource:
    def __init__(self, identity):
        self.id = int(identity.Id)
        self.manufacturer = identity.Manufacturer
        self.product_family = identity.ProductFamily
        self.product_name = identity.ProductName
        self.protocol = (int(identity.ProtocolMajor),
                         int(identity.ProtocolMinor))

    def __repr__(self):
        return f"TwainSource({self.product_name!r}, {self.manufacturer!r})"


def dsm_path():
    local = Path(__file__).resolve().parent / "bin" / (
        "TWAINDSM32.dll" if ctypes.sizeof(ctypes.c_void_p) == 4
        else "TWAINDSM.dll")
    if local.exists():
        return str(local)
    for name in ("twaindsm.dll", "twain_32.dll"):
        try:
            ctypes.WinDLL(name)
            return name
        except OSError:
            continue
    return ""


def dsm_available():
    return bool(dsm_path())


def _load_dsm():
    local = Path(__file__).resolve().parent / "bin" / (
        "TWAINDSM32.dll" if ctypes.sizeof(ctypes.c_void_p) == 4
        else "TWAINDSM.dll")
    for name in (str(local), "twaindsm.dll", "twain_32.dll"):
        try:
            library = ctypes.WinDLL(name)
        except OSError:
            continue
        entry = library.DSM_Entry
        entry.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                          wintypes.DWORD, wintypes.WORD, wintypes.WORD,
                          ctypes.c_void_p]
        entry.restype = wintypes.WORD
        return library
    return None


def list_sources():
    library = _load_dsm()
    if library is None:
        return []
    user32 = ctypes.WinDLL("user32")
    user32.GetDesktopWindow.restype = ctypes.c_void_p
    parent = ctypes.c_void_p(user32.GetDesktopWindow())
    if library.DSM_Entry(None, None, DG_CONTROL, DAT_PARENT, MSG_OPENDSM,
                         ctypes.byref(parent)) != 0:
        return []
    sources = []
    identity = TW_IDENTITY()
    result = library.DSM_Entry(None, None, DG_CONTROL, DAT_IDENTITY,
                               MSG_GETFIRST, ctypes.byref(identity))
    if result != 0:
        return sources
    while True:
        sources.append(TwainSource(identity))
        identity = TW_IDENTITY()
        result = library.DSM_Entry(None, None, DG_CONTROL, DAT_IDENTITY,
                                   MSG_GETNEXT, ctypes.byref(identity))
        if result != 0:
            break
    library.DSM_Entry(None, None, DG_CONTROL, DAT_PARENT, MSG_CLOSEDSM, None)
    return sources
