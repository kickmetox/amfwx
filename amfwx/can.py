"""CAN bus abstraction with an optional PCAN backend."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


PCAN_USBBUS1 = 0x51
PCAN_BAUD_500K = 0x001C
PCAN_BAUD_250K = 0x0011
PCAN_BAUD_125K = 0x0007
PCAN_MESSAGE_STANDARD = 0x00
PCAN_MESSAGE_RTR = 0x01
PCAN_MESSAGE_EXTENDED = 0x02


class CanError(RuntimeError):
    pass


class CanFrame:
    def __init__(self, identifier, data=b"", extended=False, remote=False):
        self.identifier = int(identifier)
        self.data = bytes(data)
        self.extended = bool(extended)
        self.remote = bool(remote)
        if len(self.data) > 8:
            raise CanError("CAN-Daten max. 8 Byte")
        if not 0 <= self.identifier <= (0x1FFFFFFF if self.extended else 0x7FF):
            raise CanError("CAN-ID ausserhalb des Bereichs")

    def __repr__(self):
        return (f"CanFrame({self.identifier:#x}, {self.data.hex()}, "
                f"extended={self.extended})")


class TPCANMsg(ctypes.Structure):
    _fields_ = [("ID", wintypes.DWORD),
                ("MSGTYPE", wintypes.WORD),
                ("LEN", ctypes.c_ubyte),
                ("DATA", ctypes.c_ubyte * 8)]


class PcanBus:
    def __init__(self, channel=PCAN_USBBUS1, baudrate=PCAN_BAUD_500K,
                 library="PCANBasic.dll"):
        try:
            self.library = ctypes.WinDLL(library)
        except OSError as error:
            raise CanError(f"PCAN-Bibliothek fehlt: {library}") from error
        self.channel = int(channel)
        self.baudrate = int(baudrate)
        self.initialized = False

    def open(self):
        result = self.library.CAN_Initialize(self.channel, self.baudrate)
        if result != 0:
            raise CanError(f"CAN_Initialize: {result:#x}")
        self.initialized = True
        return self

    def write(self, frame):
        if not self.initialized:
            raise CanError("CAN nicht geoeffnet")
        message = TPCANMsg()
        message.ID = frame.identifier
        message.MSGTYPE = (PCAN_MESSAGE_EXTENDED if frame.extended else
                           PCAN_MESSAGE_STANDARD)
        if frame.remote:
            message.MSGTYPE |= PCAN_MESSAGE_RTR
        message.LEN = len(frame.data)
        for index, byte in enumerate(frame.data):
            message.DATA[index] = byte
        result = self.library.CAN_Write(self.channel, ctypes.byref(message))
        if result != 0:
            raise CanError(f"CAN_Write: {result:#x}")
        return self

    def read(self):
        if not self.initialized:
            raise CanError("CAN nicht geoeffnet")
        message = TPCANMsg()
        result = self.library.CAN_Read(self.channel, ctypes.byref(message))
        if result != 0:
            raise CanError(f"CAN_Read: {result:#x}")
        return CanFrame(message.ID, bytes(message.DATA[:message.LEN]),
                        bool(message.MSGTYPE & PCAN_MESSAGE_EXTENDED),
                        bool(message.MSGTYPE & PCAN_MESSAGE_RTR))

    def close(self):
        if self.initialized:
            self.library.CAN_Uninitialize(self.channel)
            self.initialized = False
        return self

    def __enter__(self):
        return self.open()

    def __exit__(self, *_exc):
        self.close()
