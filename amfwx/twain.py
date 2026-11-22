"""TWAIN data-source enumeration for old and new scanners."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


DG_CONTROL = 1
DAT_IDENTITY = 1
MSG_GETFIRST = 1
MSG_GETNEXT = 2


class TW_VERSION(ctypes.Structure):
    _fields_ = [("MajorNum", wintypes.WORD),
                ("MinorNum", wintypes.WORD),
                ("Language", wintypes.WORD),
                ("Country", wintypes.WORD),
                ("Info", wintypes.WCHAR * 34)]


class TW_IDENTITY(ctypes.Structure):
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


def _load_dsm():
    for name in ("twaindsm.dll", "twain_32.dll"):
        try:
            library = ctypes.WinDLL(name)
        except OSError:
            continue
        entry = library.DSM_Entry
        entry.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                          wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                          ctypes.c_void_p]
        entry.restype = wintypes.WORD
        return library
    return None


def list_sources():
    library = _load_dsm()
    if library is None:
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
    return sources
