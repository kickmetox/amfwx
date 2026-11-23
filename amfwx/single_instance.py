"""Single-instance guard using a named Windows mutex and activation event."""

from __future__ import annotations

import ctypes
import threading
from ctypes import wintypes


ERROR_ALREADY_EXISTS = 183
EVENT_MODIFY_STATE = 0x0002
INFINITE = 0xFFFFFFFF
WAIT_OBJECT_0 = 0


class SingleInstanceError(RuntimeError):
    pass


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL,
                                  wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL,
                                  wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateEventW.restype = wintypes.HANDLE
kernel32.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL,
                                wintypes.LPCWSTR]
kernel32.OpenEventW.restype = wintypes.HANDLE
kernel32.SetEvent.argtypes = [wintypes.HANDLE]
kernel32.WaitForMultipleObjects.argtypes = [wintypes.DWORD,
                                            ctypes.POINTER(wintypes.HANDLE),
                                            wintypes.BOOL, wintypes.DWORD]
kernel32.WaitForMultipleObjects.restype = wintypes.DWORD
kernel32.ReleaseMutex.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


class SingleInstance:
    def __init__(self, name="AMFWX", on_activate=None):
        self.name = "Local\\" + str(name)
        self.event_name = self.name + "-activate"
        self.stop_name = self.name + "-stop"
        self.on_activate = on_activate
        self.handle = None
        self.event = None
        self.stop = None
        self.already_running = False
        self._thread = None

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
        if self.already_running:
            self.notify_existing()
            return False
        self.event = kernel32.CreateEventW(None, False, False, self.event_name)
        self.stop = kernel32.CreateEventW(None, False, False, self.stop_name)
        if not self.event or not self.stop:
            self.release()
            raise SingleInstanceError("CreateEventW fehlgeschlagen")
        if self.on_activate is not None:
            self._thread = threading.Thread(target=self._listen, daemon=True)
            self._thread.start()
        return True

    def _listen(self):
        handles = (wintypes.HANDLE * 2)(self.event, self.stop)
        while True:
            result = kernel32.WaitForMultipleObjects(2, handles, False,
                                                     INFINITE)
            if result != WAIT_OBJECT_0:
                break
            try:
                self.on_activate()
            except Exception:
                pass

    def notify_existing(self):
        handle = kernel32.OpenEventW(EVENT_MODIFY_STATE, False,
                                     self.event_name)
        if not handle:
            return False
        try:
            return bool(kernel32.SetEvent(handle))
        finally:
            kernel32.CloseHandle(handle)

    def release(self):
        if self.stop:
            kernel32.SetEvent(self.stop)
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        for handle in (self.event, self.stop, self.handle):
            if handle:
                kernel32.CloseHandle(handle)
        self.event = self.stop = self.handle = None
        self.already_running = False
        return self

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *_exc):
        self.release()
