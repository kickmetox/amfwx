"""Windows Bluetooth radio/device enumeration."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


class BLUETOOTH_ADDRESS(ctypes.Union):
    _fields_ = [("ullLong", ctypes.c_ulonglong),
                ("rgBytes", ctypes.c_ubyte * 6)]


class SYSTEMTIME(ctypes.Structure):
    _fields_ = [("wYear", wintypes.WORD), ("wMonth", wintypes.WORD),
                ("wDayOfWeek", wintypes.WORD), ("wDay", wintypes.WORD),
                ("wHour", wintypes.WORD), ("wMinute", wintypes.WORD),
                ("wSecond", wintypes.WORD), ("wMilliseconds", wintypes.WORD)]


class BLUETOOTH_RADIO_INFO(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD),
                ("address", BLUETOOTH_ADDRESS),
                ("szName", wintypes.WCHAR * 248),
                ("ulClassofDevice", wintypes.ULONG),
                ("lmpSubversion", wintypes.USHORT),
                ("manufacturer", wintypes.USHORT)]


class BLUETOOTH_FIND_RADIO_PARAMS(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD)]


class BLUETOOTH_DEVICE_SEARCH_PARAMS(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD),
                ("fReturnAuthenticated", wintypes.BOOL),
                ("fReturnRemembered", wintypes.BOOL),
                ("fReturnUnknown", wintypes.BOOL),
                ("fReturnConnected", wintypes.BOOL),
                ("fIssueInquiry", wintypes.BOOL),
                ("cTimeoutMultiplier", ctypes.c_ubyte),
                ("hRadio", wintypes.HANDLE)]


class BLUETOOTH_DEVICE_INFO(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD),
                ("Address", BLUETOOTH_ADDRESS),
                ("ulClassofDevice", wintypes.ULONG),
                ("fConnected", wintypes.BOOL),
                ("fRemembered", wintypes.BOOL),
                ("fAuthenticated", wintypes.BOOL),
                ("stLastSeen", SYSTEMTIME),
                ("stLastUsed", SYSTEMTIME),
                ("szName", wintypes.WCHAR * 248)]


bth = ctypes.WinDLL("BluetoothAPIs.dll", use_last_error=True)
bth.BluetoothFindFirstRadio.argtypes = [ctypes.POINTER(BLUETOOTH_FIND_RADIO_PARAMS),
                                        ctypes.POINTER(wintypes.HANDLE)]
bth.BluetoothFindFirstRadio.restype = wintypes.HANDLE
bth.BluetoothGetRadioInfo.argtypes = [wintypes.HANDLE,
                                      ctypes.POINTER(BLUETOOTH_RADIO_INFO)]
bth.BluetoothGetRadioInfo.restype = wintypes.DWORD
bth.BluetoothFindNextRadio.argtypes = [wintypes.HANDLE,
                                        ctypes.POINTER(wintypes.HANDLE)]
bth.BluetoothFindNextRadio.restype = wintypes.BOOL
bth.BluetoothFindRadioClose.argtypes = [wintypes.HANDLE]
bth.BluetoothFindFirstDevice.argtypes = [
    ctypes.POINTER(BLUETOOTH_DEVICE_SEARCH_PARAMS),
    ctypes.POINTER(BLUETOOTH_DEVICE_INFO)]
bth.BluetoothFindFirstDevice.restype = wintypes.HANDLE
bth.BluetoothFindNextDevice.argtypes = [wintypes.HANDLE,
                                        ctypes.POINTER(BLUETOOTH_DEVICE_INFO)]
bth.BluetoothFindDeviceClose.argtypes = [wintypes.HANDLE]
kernel32 = ctypes.WinDLL("kernel32")
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def _address_text(address):
    return ":".join(f"{byte:02X}" for byte in address.rgBytes)


class BluetoothRadio:
    def __init__(self, handle, info):
        self.handle = handle
        self.name = info.szName
        self.address = _address_text(info.address)
        self.manufacturer = int(info.manufacturer)

    def __repr__(self):
        return f"BluetoothRadio({self.name!r}, {self.address})"


def list_radios():
    radios = []
    params = BLUETOOTH_FIND_RADIO_PARAMS(ctypes.sizeof(BLUETOOTH_FIND_RADIO_PARAMS))
    handle = wintypes.HANDLE()
    find = bth.BluetoothFindFirstRadio(ctypes.byref(params),
                                       ctypes.byref(handle))
    if not find:
        return radios
    try:
        while True:
            info = BLUETOOTH_RADIO_INFO()
            info.dwSize = ctypes.sizeof(BLUETOOTH_RADIO_INFO)
            if bth.BluetoothGetRadioInfo(handle, ctypes.byref(info)) == 0:
                radios.append(BluetoothRadio(handle, info))
            if not bth.BluetoothFindNextRadio(find, ctypes.byref(handle)):
                break
    finally:
        bth.BluetoothFindRadioClose(find)
    return radios


def list_devices(radio=None, issue_inquiry=False, timeout_multiplier=1,
                 authenticated=True, remembered=True, unknown=True,
                 connected=True):
    devices = []
    params = BLUETOOTH_DEVICE_SEARCH_PARAMS()
    params.dwSize = ctypes.sizeof(BLUETOOTH_DEVICE_SEARCH_PARAMS)
    params.fReturnAuthenticated = bool(authenticated)
    params.fReturnRemembered = bool(remembered)
    params.fReturnUnknown = bool(unknown)
    params.fReturnConnected = bool(connected)
    params.fIssueInquiry = bool(issue_inquiry)
    params.cTimeoutMultiplier = max(1, int(timeout_multiplier))
    params.hRadio = getattr(radio, "handle", None)
    info = BLUETOOTH_DEVICE_INFO()
    info.dwSize = ctypes.sizeof(BLUETOOTH_DEVICE_INFO)
    find = bth.BluetoothFindFirstDevice(ctypes.byref(params),
                                        ctypes.byref(info))
    if not find:
        return devices
    try:
        while True:
            devices.append({
                "name": info.szName,
                "address": _address_text(info.Address),
                "connected": bool(info.fConnected),
                "remembered": bool(info.fRemembered),
                "authenticated": bool(info.fAuthenticated),
            })
            if not bth.BluetoothFindNextDevice(find, ctypes.byref(info)):
                break
    finally:
        bth.BluetoothFindDeviceClose(find)
    return devices
