"""LIN bus abstraction with an optional PCAN-LIN backend."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


PCAN_LINBUS1 = 0x55


class LinError(RuntimeError):
    pass


class LinFrame:
    def __init__(self, identifier, data=b""):
        self.identifier = int(identifier)
        self.data = bytes(data)
        if not 0 <= self.identifier <= 0x3F:
            raise LinError("LIN-ID muss 0..0x3F sein")
        if not 1 <= len(self.data) <= 8:
            raise LinError("LIN-Daten muessen 1..8 Byte sein")

    def __repr__(self):
        return f"LinFrame({self.identifier:#x}, {self.data.hex()})"


class TPCANMsg(ctypes.Structure):
    _fields_ = [("ID", wintypes.DWORD),
                ("MSGTYPE", wintypes.WORD),
                ("LEN", ctypes.c_ubyte),
                ("DATA", ctypes.c_ubyte * 8)]


class PcanLin:
    def __init__(self, channel=PCAN_LINBUS1, baudrate=19200,
                 library="PCANBasic.dll"):
        try:
            self.library = ctypes.WinDLL(library)
        except OSError as error:
            raise LinError(f"PCAN-Bibliothek fehlt: {library}") from error
        self.channel = int(channel)
        self.baudrate = int(baudrate)
        self.initialized = False

    def open(self):
        result = self.library.LIN_Initialize(self.channel, self.baudrate)
        if result != 0:
            raise LinError(f"LIN_Initialize: {result:#x}")
        self.initialized = True
        return self

    def write(self, frame):
        if not self.initialized:
            raise LinError("LIN nicht geoeffnet")
        message = TPCANMsg()
        message.ID = frame.identifier
        message.LEN = len(frame.data)
        for index, byte in enumerate(frame.data):
            message.DATA[index] = byte
        result = self.library.LIN_Write(self.channel, ctypes.byref(message))
        if result != 0:
            raise LinError(f"LIN_Write: {result:#x}")
        return self

    def read(self):
        if not self.initialized:
            raise LinError("LIN nicht geoeffnet")
        message = TPCANMsg()
        result = self.library.LIN_Read(self.channel, ctypes.byref(message))
        if result != 0:
            raise LinError(f"LIN_Read: {result:#x}")
        return LinFrame(message.ID, bytes(message.DATA[:message.LEN]))

    def close(self):
        if self.initialized:
            self.library.LIN_Uninitialize(self.channel)
            self.initialized = False
        return self

    def __enter__(self):
        return self.open()

    def __exit__(self, *_exc):
        self.close()
