"""Windows serial/UART access via Win32."""

from __future__ import annotations

import ctypes
import time
import winreg
from ctypes import wintypes


GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
PURGE_TXCLEAR = 0x0004
PURGE_RXCLEAR = 0x0008
MAXDWORD = 0xFFFFFFFF


class SerialError(RuntimeError):
    pass


class DCB(ctypes.Structure):
    _fields_ = [
        ("DCBlength", wintypes.DWORD),
        ("BaudRate", wintypes.DWORD),
        ("fBinary", wintypes.DWORD, 1),
        ("fParity", wintypes.DWORD, 1),
        ("fOutxCtsFlow", wintypes.DWORD, 1),
        ("fOutxDsrFlow", wintypes.DWORD, 1),
        ("fDtrControl", wintypes.DWORD, 2),
        ("fDsrSensitivity", wintypes.DWORD, 1),
        ("fTXContinueOnXoff", wintypes.DWORD, 1),
        ("fOutX", wintypes.DWORD, 1),
        ("fInX", wintypes.DWORD, 1),
        ("fErrorChar", wintypes.DWORD, 1),
        ("fNull", wintypes.DWORD, 1),
        ("fRtsControl", wintypes.DWORD, 2),
        ("fAbortOnError", wintypes.DWORD, 1),
        ("fDummy2", wintypes.DWORD, 17),
        ("wReserved", wintypes.WORD),
        ("XonLim", wintypes.WORD),
        ("XoffLim", wintypes.WORD),
        ("ByteSize", wintypes.BYTE),
        ("Parity", wintypes.BYTE),
        ("StopBits", wintypes.BYTE),
        ("XonChar", ctypes.c_char),
        ("XoffChar", ctypes.c_char),
        ("ErrorChar", ctypes.c_char),
        ("EofChar", ctypes.c_char),
        ("EvtChar", ctypes.c_char),
        ("wReserved1", wintypes.WORD),
    ]


class COMMTIMEOUTS(ctypes.Structure):
    _fields_ = [
        ("ReadIntervalTimeout", wintypes.DWORD),
        ("ReadTotalTimeoutMultiplier", wintypes.DWORD),
        ("ReadTotalTimeoutConstant", wintypes.DWORD),
        ("WriteTotalTimeoutMultiplier", wintypes.DWORD),
        ("WriteTotalTimeoutConstant", wintypes.DWORD),
    ]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                 wintypes.DWORD, ctypes.c_void_p,
                                 wintypes.DWORD, wintypes.DWORD,
                                 wintypes.HANDLE]
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.GetCommState.argtypes = [wintypes.HANDLE, ctypes.POINTER(DCB)]
kernel32.SetCommState.argtypes = [wintypes.HANDLE, ctypes.POINTER(DCB)]
kernel32.SetCommTimeouts.argtypes = [wintypes.HANDLE,
                                     ctypes.POINTER(COMMTIMEOUTS)]
kernel32.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                              wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                              ctypes.c_void_p]
kernel32.WriteFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                               wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                               ctypes.c_void_p]
kernel32.PurgeComm.argtypes = [wintypes.HANDLE, wintypes.DWORD]


def list_ports():
    ports = []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"HARDWARE\DEVICEMAP\SERIALCOMM")
    except OSError:
        return ports
    try:
        index = 0
        while True:
            try:
                _name, value, _kind = winreg.EnumValue(key, index)
            except OSError:
                break
            ports.append(str(value))
            index += 1
    finally:
        winreg.CloseKey(key)
    return sorted(set(ports))


class SerialPort:
    def __init__(self, port, baudrate=115200, timeout=1.0,
                 bytesize=8, parity="N", stopbits=1):
        self.port = str(port)
        self.baudrate = int(baudrate)
        self.timeout = float(timeout)
        self.bytesize = int(bytesize)
        self.parity = str(parity).upper()
        self.stopbits = int(stopbits)
        self.handle = None

    def _dcb(self):
        dcb = DCB()
        dcb.DCBlength = ctypes.sizeof(DCB)
        dcb.BaudRate = self.baudrate
        dcb.ByteSize = self.bytesize
        dcb.Parity = {"N": 0, "O": 1, "E": 2, "M": 3, "S": 4}.get(
            self.parity, 0)
        dcb.StopBits = {1: 0, 2: 2}.get(self.stopbits, 0)
        dcb.fBinary = 1
        dcb.fParity = 0
        dcb.fOutxCtsFlow = 0
        dcb.fOutxDsrFlow = 0
        dcb.fDtrControl = 1
        dcb.fRtsControl = 1
        return dcb

    def open(self):
        path = self.port if self.port.startswith("\\\\.\\") else f"\\\\.\\{self.port}"
        handle = kernel32.CreateFileW(path, GENERIC_READ | GENERIC_WRITE,
                                      0, None, OPEN_EXISTING, 0, None)
        if handle == INVALID_HANDLE_VALUE or handle is None:
            raise SerialError(f"COM-Port nicht offen: {self.port}")
        self.handle = handle
        dcb = self._dcb()
        if not kernel32.SetCommState(handle, ctypes.byref(dcb)):
            self.close()
            raise SerialError(f"SetCommState fehlgeschlagen: {self.port}")
        timeouts = COMMTIMEOUTS()
        timeouts.ReadIntervalTimeout = 50
        timeouts.ReadTotalTimeoutMultiplier = 0
        timeouts.ReadTotalTimeoutConstant = max(1, int(self.timeout * 1000))
        timeouts.WriteTotalTimeoutMultiplier = 0
        timeouts.WriteTotalTimeoutConstant = max(1, int(self.timeout * 1000))
        kernel32.SetCommTimeouts(handle, ctypes.byref(timeouts))
        kernel32.PurgeComm(handle, PURGE_RXCLEAR | PURGE_TXCLEAR)
        return self

    def _require(self):
        if self.handle is None:
            raise SerialError("Port nicht geoeffnet")

    def write(self, data):
        self._require()
        payload = bytes(data)
        written = wintypes.DWORD(0)
        buffer = ctypes.create_string_buffer(payload, len(payload))
        if not kernel32.WriteFile(self.handle, buffer, len(payload),
                                  ctypes.byref(written), None):
            raise SerialError("WriteFile fehlgeschlagen")
        return int(written.value)

    def read(self, size=1):
        self._require()
        buffer = ctypes.create_string_buffer(int(size))
        read = wintypes.DWORD(0)
        if not kernel32.ReadFile(self.handle, buffer, int(size),
                                 ctypes.byref(read), None):
            raise SerialError("ReadFile fehlgeschlagen")
        return buffer.raw[:read.value]

    def flush(self):
        self._require()
        kernel32.PurgeComm(self.handle, PURGE_RXCLEAR | PURGE_TXCLEAR)
        return self

    def close(self):
        if self.handle is not None:
            kernel32.CloseHandle(self.handle)
            self.handle = None
        return self

    def __enter__(self):
        return self.open()

    def __exit__(self, *_exc):
        self.close()
