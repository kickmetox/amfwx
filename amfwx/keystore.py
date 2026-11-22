"""DPAPI-backed key store for Windows."""

from __future__ import annotations

import ctypes
import os
import re
from ctypes import POINTER, byref, c_void_p
from pathlib import Path


class KeyStoreError(RuntimeError):
    pass


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_uint), ("pbData", c_void_p)]


crypt32 = ctypes.WinDLL("crypt32")
kernel32 = ctypes.WinDLL("kernel32")
crypt32.CryptProtectData.argtypes = [POINTER(DATA_BLOB), ctypes.c_wchar_p,
                                     POINTER(DATA_BLOB), c_void_p, c_void_p,
                                     ctypes.c_uint, POINTER(DATA_BLOB)]
crypt32.CryptProtectData.restype = ctypes.c_bool
crypt32.CryptUnprotectData.argtypes = [POINTER(DATA_BLOB), c_void_p,
                                       POINTER(DATA_BLOB), c_void_p, c_void_p,
                                       ctypes.c_uint, POINTER(DATA_BLOB)]
crypt32.CryptUnprotectData.restype = ctypes.c_bool
kernel32.LocalFree.argtypes = [c_void_p]


def default_key_dir():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    return base / "AMFWX" / "keys"


class KeyStore:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory else default_key_dir()
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, name):
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", str(name)):
            raise KeyStoreError(f"ungueltiger Key-Name: {name!r}")
        return self.directory / f"{name}.bin"

    def _blob(self, data):
        buffer = ctypes.create_string_buffer(data, len(data))
        blob = DATA_BLOB(len(data), ctypes.cast(buffer, c_void_p))
        return buffer, blob

    def save(self, name, secret):
        data = str(secret).encode("utf-8")
        in_buffer, in_blob = self._blob(data)
        out_blob = DATA_BLOB()
        if not crypt32.CryptProtectData(byref(in_blob), "AMFWX", None, None,
                                        None, 0, byref(out_blob)):
            raise KeyStoreError("CryptProtectData fehlgeschlagen")
        try:
            encrypted = ctypes.string_at(out_blob.pbData, out_blob.cbData)
            self._path(name).write_bytes(encrypted)
        finally:
            kernel32.LocalFree(out_blob.pbData)
        return self

    def load(self, name):
        path = self._path(name)
        if not path.exists():
            return None
        data = path.read_bytes()
        in_buffer, in_blob = self._blob(data)
        out_blob = DATA_BLOB()
        if not crypt32.CryptUnprotectData(byref(in_blob), None, None, None,
                                          None, 0, byref(out_blob)):
            raise KeyStoreError("CryptUnprotectData fehlgeschlagen")
        try:
            return ctypes.string_at(out_blob.pbData,
                                    out_blob.cbData).decode("utf-8")
        finally:
            kernel32.LocalFree(out_blob.pbData)

    def delete(self, name):
        try:
            self._path(name).unlink()
            return True
        except FileNotFoundError:
            return False

    def names(self):
        return sorted(path.stem for path in self.directory.glob("*.bin"))
