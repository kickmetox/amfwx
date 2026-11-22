"""Windows WLAN interface and network scanning."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]


class DOT11_SSID(ctypes.Structure):
    _fields_ = [("uSSIDLength", wintypes.ULONG),
                ("ucSSID", ctypes.c_ubyte * 32)]


class WLAN_INTERFACE_INFO(ctypes.Structure):
    _fields_ = [("InterfaceGuid", GUID),
                ("strInterfaceDescription", wintypes.WCHAR * 256),
                ("isState", wintypes.DWORD)]


class WLAN_INTERFACE_INFO_LIST(ctypes.Structure):
    _fields_ = [("dwNumberOfItems", wintypes.DWORD),
                ("dwIndex", wintypes.DWORD),
                ("InterfaceInfo", WLAN_INTERFACE_INFO * 1)]


class WLAN_AVAILABLE_NETWORK(ctypes.Structure):
    _fields_ = [
        ("strProfileName", wintypes.WCHAR * 256),
        ("dot11Ssid", DOT11_SSID),
        ("dot11BssType", wintypes.DWORD),
        ("uNumberOfBssids", wintypes.ULONG),
        ("bNetworkConnectable", wintypes.BOOL),
        ("wlanNotConnectableReason", wintypes.DWORD),
        ("uNumberOfPhyTypes", wintypes.ULONG),
        ("dot11PhyTypes", wintypes.DWORD * 8),
        ("bMorePhyTypes", wintypes.BOOL),
        ("wlanSignalQuality", wintypes.ULONG),
        ("bSecurityEnabled", wintypes.BOOL),
        ("dot11DefaultAuthAlgorithm", wintypes.DWORD),
        ("dot11DefaultCipherAlgorithm", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("dwReserved", wintypes.DWORD),
    ]


class WLAN_AVAILABLE_NETWORK_LIST(ctypes.Structure):
    _fields_ = [("dwNumberOfItems", wintypes.DWORD),
                ("dwIndex", wintypes.DWORD),
                ("Network", WLAN_AVAILABLE_NETWORK * 1)]


wlan = ctypes.WinDLL("wlanapi.dll", use_last_error=True)
wlan.WlanOpenHandle.argtypes = [wintypes.DWORD, ctypes.c_void_p,
                                ctypes.POINTER(wintypes.DWORD),
                                ctypes.POINTER(wintypes.HANDLE)]
wlan.WlanOpenHandle.restype = wintypes.DWORD
wlan.WlanCloseHandle.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
wlan.WlanEnumInterfaces.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                    ctypes.POINTER(ctypes.POINTER(
                                        WLAN_INTERFACE_INFO_LIST))]
wlan.WlanEnumInterfaces.restype = wintypes.DWORD
wlan.WlanGetAvailableNetworkList.argtypes = [
    wintypes.HANDLE, ctypes.POINTER(GUID), wintypes.DWORD,
    ctypes.c_void_p, ctypes.POINTER(ctypes.POINTER(
        WLAN_AVAILABLE_NETWORK_LIST))]
wlan.WlanGetAvailableNetworkList.restype = wintypes.DWORD
wlan.WlanFreeMemory.argtypes = [ctypes.c_void_p]


class WlanError(RuntimeError):
    pass


class WlanInterface:
    def __init__(self, guid, description, state):
        self.guid = guid
        self.description = description
        self.state = int(state)

    def __repr__(self):
        return f"WlanInterface({self.description!r})"


class WlanNetwork:
    def __init__(self, ssid, quality, secure, connectable, profile=""):
        self.ssid = ssid
        self.quality = int(quality)
        self.secure = bool(secure)
        self.connectable = bool(connectable)
        self.profile = profile

    def __repr__(self):
        return (f"WlanNetwork({self.ssid!r}, {self.quality}%"
                f"{', secure' if self.secure else ''})")


def _open():
    version = wintypes.DWORD()
    handle = wintypes.HANDLE()
    code = wlan.WlanOpenHandle(2, None, ctypes.byref(version),
                               ctypes.byref(handle))
    if code:
        raise WlanError(f"WlanOpenHandle: {code}")
    return handle


def list_interfaces():
    handle = _open()
    result = []
    try:
        pointer = ctypes.POINTER(WLAN_INTERFACE_INFO_LIST)()
        code = wlan.WlanEnumInterfaces(handle, None, ctypes.byref(pointer))
        if code:
            raise WlanError(f"WlanEnumInterfaces: {code}")
        try:
            count = pointer.contents.dwNumberOfItems
            base = ctypes.addressof(pointer.contents) + 2 * ctypes.sizeof(wintypes.DWORD)
            items = (WLAN_INTERFACE_INFO * count).from_address(base)
            for info in items:
                result.append(WlanInterface(info.InterfaceGuid,
                                            info.strInterfaceDescription,
                                            info.isState))
        finally:
            wlan.WlanFreeMemory(pointer)
    finally:
        wlan.WlanCloseHandle(handle, None)
    return result


def _ssid_text(ssid):
    length = max(0, min(32, int(ssid.uSSIDLength)))
    raw = bytes(ssid.ucSSID[:length])
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", "replace")


def scan(interface=None):
    handle = _open()
    result = []
    try:
        if interface is None:
            interfaces = list_interfaces()
            if not interfaces:
                return result
            interface = interfaces[0]
        pointer = ctypes.POINTER(WLAN_AVAILABLE_NETWORK_LIST)()
        code = wlan.WlanGetAvailableNetworkList(
            handle, ctypes.byref(interface.guid), 3, None,
            ctypes.byref(pointer))
        if code:
            raise WlanError(f"WlanGetAvailableNetworkList: {code}")
        try:
            count = pointer.contents.dwNumberOfItems
            base = ctypes.addressof(pointer.contents) + 2 * ctypes.sizeof(wintypes.DWORD)
            items = (WLAN_AVAILABLE_NETWORK * count).from_address(base)
            for network in items:
                result.append(WlanNetwork(
                    _ssid_text(network.dot11Ssid),
                    network.wlanSignalQuality,
                    network.bSecurityEnabled,
                    network.bNetworkConnectable,
                    network.strProfileName))
        finally:
            wlan.WlanFreeMemory(pointer)
    finally:
        wlan.WlanCloseHandle(handle, None)
    return result
