"""32-bit TWAIN helper for 32-bit-only scanner drivers.

Run with a 32-bit Python:

    vendor/python32/python.exe tools/twain32_helper.py --list
"""

from __future__ import annotations

import argparse
import ctypes
import json
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DSM = Path(r"C:\Windows\twain_32.dll") if Path(r"C:\Windows\twain_32.dll").exists() else ROOT / "amfwx" / "bin" / "TWAINDSM32.dll"


DG_CONTROL = 1
DG_IMAGE = 2
DAT_EVENT = 2
DAT_IDENTITY = 3
DAT_PARENT = 4
DAT_PENDINGXFERS = 5
DAT_USERINTERFACE = 9
DAT_IMAGENATIVEXFER = 0x0104
MSG_GET = 1
MSG_OPENDSM = 0x0301
MSG_CLOSEDSM = 0x0302
MSG_OPENDS = 0x0401
MSG_CLOSEDS = 0x0402
MSG_ENABLEDS = 0x0502
MSG_DISABLEDS = 0x0501
MSG_PROCESSEVENT = 0x0601
MSG_ENDXFER = 0x0701
MSG_GETFIRST = 4
MSG_GETNEXT = 5
TWRC_SUCCESS = 0
TWRC_DSEVENT = 4
TWRC_XFERDONE = 6
TWRC_ENDOFLIST = 7
TWMSG_XFERREADY = 0x0101
TWMSG_CLOSEREQ = 0x0102
PM_REMOVE = 0x0001


class TW_VERSION(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("MajorNum", wintypes.WORD), ("MinorNum", wintypes.WORD),
                ("Language", wintypes.WORD), ("Country", wintypes.WORD),
                ("Info", ctypes.c_char * 34)]


class TW_IDENTITY(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("Id", wintypes.ULONG), ("Version", TW_VERSION),
                ("ProtocolMajor", wintypes.WORD),
                ("ProtocolMinor", wintypes.WORD),
                ("SupportedGroups", wintypes.ULONG),
                ("Manufacturer", ctypes.c_char * 34),
                ("ProductFamily", ctypes.c_char * 34),
                ("ProductName", ctypes.c_char * 34)]


class TW_USERINTERFACE(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("ShowUI", wintypes.WORD), ("ModalUI", wintypes.WORD),
                ("hParent", ctypes.c_void_p)]


class TW_EVENT(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("pEvent", ctypes.c_void_p), ("TWMessage", wintypes.WORD)]


class TW_PENDINGXFERS(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("Count", wintypes.WORD), ("Reserved", wintypes.DWORD)]


def text(value):
    if isinstance(value, bytes):
        return value.decode("mbcs", "replace").rstrip("\x00")
    return str(value).rstrip("\x00")


def app_identity():
    app = TW_IDENTITY()
    app.ProductName = b"AMFWX"
    app.Manufacturer = b"AMFWX"
    app.ProductFamily = b"AMFWX"
    app.SupportedGroups = 0x0003
    app.ProtocolMajor = 2
    app.ProtocolMinor = 5
    app.Version.MajorNum = 1
    return app


def load():
    if not DSM.exists():
        raise RuntimeError(f"fehlt: {DSM}")
    lib = ctypes.WinDLL(str(DSM))
    lib.DSM_Entry.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                              wintypes.DWORD, wintypes.WORD, wintypes.WORD,
                              ctypes.c_void_p]
    lib.DSM_Entry.restype = wintypes.WORD
    return lib


def source_list():
    lib = load()
    user32 = ctypes.WinDLL("user32")
    user32.GetDesktopWindow.restype = ctypes.c_void_p
    parent = ctypes.c_void_p(user32.GetDesktopWindow())
    app = app_identity()
    if lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL, DAT_PARENT,
                     MSG_OPENDSM, ctypes.byref(parent)) != TWRC_SUCCESS:
        raise RuntimeError("OPENDSM fehlgeschlagen")
    result = []
    try:
        identity = TW_IDENTITY()
        rc = lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL, DAT_IDENTITY,
                           MSG_GETFIRST, ctypes.byref(identity))
        while rc == TWRC_SUCCESS:
            result.append({"id": int(identity.Id),
                           "name": text(identity.ProductName),
                           "manufacturer": text(identity.Manufacturer)})
            identity = TW_IDENTITY()
            rc = lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL,
                               DAT_IDENTITY, MSG_GETNEXT,
                               ctypes.byref(identity))
        if rc not in (TWRC_ENDOFLIST, TWRC_SUCCESS):
            raise RuntimeError(f"GETFIRST/GETNEXT: {rc}")
    finally:
        lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL, DAT_PARENT,
                      MSG_CLOSEDSM, None)
    return result


def find_source(lib, app, wanted):
    identity = TW_IDENTITY()
    rc = lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL, DAT_IDENTITY,
                       MSG_GETFIRST, ctypes.byref(identity))
    while rc == TWRC_SUCCESS:
        name = text(identity.ProductName)
        if str(wanted) in (name, str(identity.Id)):
            return identity
        identity = TW_IDENTITY()
        rc = lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL, DAT_IDENTITY,
                           MSG_GETNEXT, ctypes.byref(identity))
    raise RuntimeError(f"Quelle nicht gefunden: {wanted}")


def dib_to_bmp(dib):
    if len(dib) < 40:
        raise RuntimeError("DIB zu kurz")
    header_size = struct.unpack("<I", dib[:4])[0]
    bit_count = struct.unpack("<H", dib[14:16])[0]
    palette = 0 if bit_count > 8 else (1 << bit_count) * 4
    offset = 14 + header_size + palette
    return b"BM" + struct.pack("<IHHI", 14 + len(dib), 0, 0, offset) + dib


def scan(source, path, show_ui=False, timeout=60.0):
    lib = load()
    user32 = ctypes.WinDLL("user32")
    kernel32 = ctypes.WinDLL("kernel32")
    user32.GetDesktopWindow.restype = ctypes.c_void_p
    user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG),
                                    wintypes.HWND, wintypes.UINT,
                                    wintypes.UINT, wintypes.UINT]
    user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalSize.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalSize.restype = ctypes.c_size_t
    parent = ctypes.c_void_p(user32.GetDesktopWindow())
    app = app_identity()
    if lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL, DAT_PARENT,
                     MSG_OPENDSM, ctypes.byref(parent)) != TWRC_SUCCESS:
        raise RuntimeError("OPENDSM fehlgeschlagen")
    identity = None
    opened = False
    try:
        identity = find_source(lib, app, source)
        if lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL,
                         DAT_IDENTITY, MSG_OPENDS,
                         ctypes.byref(identity)) != TWRC_SUCCESS:
            raise RuntimeError("OPENDS fehlgeschlagen")
        opened = True
        ui = TW_USERINTERFACE(1 if show_ui else 0, 0, parent)
        if lib.DSM_Entry(ctypes.byref(app), ctypes.byref(identity), DG_CONTROL,
                         DAT_USERINTERFACE, MSG_ENABLEDS,
                         ctypes.byref(ui)) != TWRC_SUCCESS:
            raise RuntimeError("ENABLEDS fehlgeschlagen")
        message = wintypes.MSG()
        event = TW_EVENT(ctypes.cast(ctypes.pointer(message), ctypes.c_void_p),
                         0)
        deadline = time.monotonic() + float(timeout)
        try:
            while True:
                if time.monotonic() > deadline:
                    raise RuntimeError("Transfer-Timeout")
                if not user32.PeekMessageW(ctypes.byref(message), None, 0, 0,
                                           PM_REMOVE):
                    time.sleep(0.01)
                    continue
                event.TWMessage = 0
                rc = lib.DSM_Entry(ctypes.byref(app),
                                   ctypes.byref(identity), DG_CONTROL,
                                   DAT_EVENT, MSG_PROCESSEVENT,
                                   ctypes.pointer(event))
                if rc == 5:
                    user32.TranslateMessage(ctypes.byref(message))
                    user32.DispatchMessageW(ctypes.byref(message))
                if event.TWMessage == 0x0101:
                    handle = wintypes.HANDLE()
                    rc = lib.DSM_Entry(ctypes.byref(app),
                                       ctypes.byref(identity), DG_IMAGE,
                                       DAT_IMAGENATIVEXFER, MSG_GET,
                                       ctypes.byref(handle))
                    if rc != TWRC_XFERDONE:
                        raise RuntimeError(f"Transfer: {rc}")
                    pointer = kernel32.GlobalLock(handle)
                    try:
                        size = kernel32.GlobalSize(handle)
                        dib = ctypes.string_at(pointer, size)
                    finally:
                        kernel32.GlobalUnlock(handle)
                    Path(path).write_bytes(dib_to_bmp(dib))
                    pending = TW_PENDINGXFERS()
                    lib.DSM_Entry(ctypes.byref(app), ctypes.byref(identity),
                                  DG_CONTROL, DAT_PENDINGXFERS, MSG_ENDXFER,
                                  ctypes.byref(pending))
                    return str(path)
                if event.TWMessage in (0x0102, 0x0103):
                    raise RuntimeError("Scanner hat den Vorgang beendet")
        finally:
            lib.DSM_Entry(ctypes.byref(app), ctypes.byref(identity),
                          DG_CONTROL, DAT_USERINTERFACE, MSG_DISABLEDS,
                          ctypes.byref(ui))
    finally:
        if opened and identity is not None:
            lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL,
                          DAT_IDENTITY, MSG_CLOSEDS, ctypes.byref(identity))
        lib.DSM_Entry(ctypes.byref(app), None, DG_CONTROL, DAT_PARENT,
                      MSG_CLOSEDSM, None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--source", default="")
    parser.add_argument("--path", default="")
    parser.add_argument("--ui", action="store_true")
    args = parser.parse_args()
    try:
        if args.list:
            print(json.dumps({"sources": source_list()}))
        elif args.scan:
            print(json.dumps({"path": scan(args.source, args.path, args.ui)}))
        else:
            print(json.dumps({"error": "list or scan required"}))
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"error": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
