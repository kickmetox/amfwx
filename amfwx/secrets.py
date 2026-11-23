"""Windows DPAPI helpers for local secrets."""

from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes


class DpapiError(RuntimeError):
    pass


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD),
                ("pbData", ctypes.POINTER(ctypes.c_byte))]


crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
crypt32.CryptProtectData.argtypes = [
    ctypes.POINTER(DATA_BLOB), wintypes.LPCWSTR, ctypes.POINTER(DATA_BLOB),
    ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD,
    ctypes.POINTER(DATA_BLOB)]
crypt32.CryptProtectData.restype = wintypes.BOOL
crypt32.CryptUnprotectData.argtypes = [
    ctypes.POINTER(DATA_BLOB), ctypes.POINTER(wintypes.LPWSTR),
    ctypes.POINTER(DATA_BLOB), ctypes.c_void_p, ctypes.c_void_p,
    wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
crypt32.CryptUnprotectData.restype = wintypes.BOOL
kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
kernel32.LocalFree.restype = wintypes.HLOCAL


def _blob(data):
    buffer = ctypes.create_string_buffer(data, len(data))
    return DATA_BLOB(len(data),
                     ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)))


def protect(data):
    source = _blob(bytes(data))
    target = DATA_BLOB()
    if not crypt32.CryptProtectData(
            ctypes.byref(source), "AMFWX", None, None, None, 0x1,
            ctypes.byref(target)):
        raise DpapiError(f"CryptProtectData: {ctypes.get_last_error()}")
    try:
        return ctypes.string_at(target.pbData, target.cbData)
    finally:
        kernel32.LocalFree(target.pbData)


def unprotect(data):
    source = _blob(bytes(data))
    target = DATA_BLOB()
    if not crypt32.CryptUnprotectData(
            ctypes.byref(source), None, None, None, None, 0x1,
            ctypes.byref(target)):
        raise DpapiError(f"CryptUnprotectData: {ctypes.get_last_error()}")
    try:
        return ctypes.string_at(target.pbData, target.cbData)
    finally:
        kernel32.LocalFree(target.pbData)


def protect_text(value):
    return "dpapi:" + base64.b64encode(
        protect(str(value).encode("utf-8"))).decode("ascii")


def unprotect_text(value):
    if not str(value).startswith("dpapi:"):
        return value
    raw = base64.b64decode(str(value)[6:])
    return unprotect(raw).decode("utf-8")
