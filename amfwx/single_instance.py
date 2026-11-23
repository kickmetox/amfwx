"""Single-instance guard using a named Windows mutex."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


ERROR_ALREADY_EXISTS = 183


class SingleInstanceError(RuntimeError):
    pass


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL,
                                  wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.ReleaseMutex.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


class SingleInstance:
    def __init__(self, name="AMFWX"):
        self.name = "Local\\" + str(name)
        self.handle = None
        self.already_running = False

    def acquire(self):
        if self.handle is not None:
            return not self.already_running
        ctypes.set_last_error(0)
        handle = kernel32.CreateMutexW(None, False, self.name)
        if not handle:
            raise SingleInstanceError("CreateMutexW fehlgeschlagen")
        error = ctypes.get_last_error()
        self.handle = handle
        self.already_running = error == ERROR_ALREADY_EXISTS
        return not self.already_running

    def release(self):
        if self.handle is not None:
            kernel32.ReleaseMutex(self.handle)
            kernel32.CloseHandle(self.handle)
            self.handle = None
        self.already_running = False
        return self

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *_exc):
        self.release()
