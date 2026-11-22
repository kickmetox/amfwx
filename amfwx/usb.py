"""Windows USB HID enumeration and raw report I/O."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


DIGCF_PRESENT = 0x00000002
DIGCF_DEVICEINTERFACE = 0x00000010
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]


class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD),
                ("InterfaceClassGuid", GUID),
                ("Flags", wintypes.DWORD),
                ("Reserved", ctypes.c_void_p)]


class SP_DEVICE_INTERFACE_DETAIL_DATA_W(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD),
                ("DevicePath", wintypes.WCHAR * 1)]


class HIDD_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Size", wintypes.DWORD),
                ("VendorID", wintypes.USHORT),
                ("ProductID", wintypes.USHORT),
                ("VersionNumber", wintypes.USHORT)]


HID_GUID = GUID(0x4D1E55B2, 0xF16F, 0x11CF,
                (0x88, 0xCB, 0x00, 0x11, 0x11, 0x00, 0x00, 0x30))

setupapi = ctypes.WinDLL("setupapi.dll", use_last_error=True)
setupapi.SetupDiGetClassDevsW.argtypes = [ctypes.POINTER(GUID),
                                          wintypes.LPCWSTR, wintypes.HWND,
                                          wintypes.DWORD]
setupapi.SetupDiGetClassDevsW.restype = wintypes.HANDLE
setupapi.SetupDiEnumDeviceInterfaces.argtypes = [
    wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(GUID),
    wintypes.DWORD, ctypes.POINTER(SP_DEVICE_INTERFACE_DATA)]
setupapi.SetupDiGetDeviceInterfaceDetailW.argtypes = [
    wintypes.HANDLE, ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
    ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
    ctypes.c_void_p]
setupapi.SetupDiDestroyDeviceInfoList.argtypes = [wintypes.HANDLE]

hid = ctypes.WinDLL("hid.dll", use_last_error=True)
hid.HidD_GetAttributes.argtypes = [wintypes.HANDLE,
                                   ctypes.POINTER(HIDD_ATTRIBUTES)]
hid.HidD_GetProductString.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                      wintypes.ULONG]
hid.HidD_GetManufacturerString.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                           wintypes.ULONG]
hid.HidD_GetSerialNumberString.argtypes = [wintypes.HANDLE,
                                           ctypes.c_void_p, wintypes.ULONG]
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                 wintypes.DWORD, ctypes.c_void_p,
                                 wintypes.DWORD, wintypes.DWORD,
                                 wintypes.HANDLE]
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                              wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                              ctypes.c_void_p]
kernel32.WriteFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                               wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                               ctypes.c_void_p]


class UsbError(RuntimeError):
    pass


class HidDeviceInfo:
    def __init__(self, path, vendor_id, product_id, product, manufacturer,
                 serial):
        self.path = path
        self.vendor_id = int(vendor_id)
        self.product_id = int(product_id)
        self.product = product
        self.manufacturer = manufacturer
        self.serial = serial

    def __repr__(self):
        return (f"HidDeviceInfo({self.vendor_id:04X}:{self.product_id:04X}, "
                f"{self.product!r})")


def _hid_string(handle, function):
    buffer = ctypes.create_unicode_buffer(256)
    if function(handle, ctypes.cast(buffer, ctypes.c_void_p),
                ctypes.sizeof(buffer)):
        return buffer.value
    return ""


def _device_info(path):
    handle = kernel32.CreateFileW(path, GENERIC_READ | GENERIC_WRITE, 3,
                                  None, OPEN_EXISTING, 0, None)
    if handle == INVALID_HANDLE_VALUE or handle is None:
        return None
    try:
        attributes = HIDD_ATTRIBUTES()
        attributes.Size = ctypes.sizeof(HIDD_ATTRIBUTES)
        if not hid.HidD_GetAttributes(handle, ctypes.byref(attributes)):
            return None
        return HidDeviceInfo(
            path, attributes.VendorID, attributes.ProductID,
            _hid_string(handle, hid.HidD_GetProductString),
            _hid_string(handle, hid.HidD_GetManufacturerString),
            _hid_string(handle, hid.HidD_GetSerialNumberString))
    finally:
        kernel32.CloseHandle(handle)


def list_hid_devices():
    handle = setupapi.SetupDiGetClassDevsW(ctypes.byref(HID_GUID), None, None,
                                           DIGCF_PRESENT | DIGCF_DEVICEINTERFACE)
    if handle == INVALID_HANDLE_VALUE or handle is None:
        return []
    devices = []
    try:
        index = 0
        while True:
            interface = SP_DEVICE_INTERFACE_DATA()
            interface.cbSize = ctypes.sizeof(SP_DEVICE_INTERFACE_DATA)
            if not setupapi.SetupDiEnumDeviceInterfaces(
                    handle, None, ctypes.byref(HID_GUID), index,
                    ctypes.byref(interface)):
                break
            index += 1
            required = wintypes.DWORD()
            setupapi.SetupDiGetDeviceInterfaceDetailW(
                handle, ctypes.byref(interface), None, 0,
                ctypes.byref(required), None)
            if required.value == 0:
                continue
            buffer = ctypes.create_string_buffer(required.value)
            detail = ctypes.cast(buffer,
                                 ctypes.POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA_W))
            detail.contents.cbSize = 8 if ctypes.sizeof(
                ctypes.c_void_p) == 8 else 6
            if not setupapi.SetupDiGetDeviceInterfaceDetailW(
                    handle, ctypes.byref(interface), buffer, required.value,
                    ctypes.byref(required), None):
                continue
            path = ctypes.wstring_at(ctypes.addressof(buffer) + 4)
            info = _device_info(path)
            if info is not None:
                devices.append(info)
    finally:
        setupapi.SetupDiDestroyDeviceInfoList(handle)
    return devices


class HidDevice:
    def __init__(self, path):
        self.path = str(path)
        self.handle = None

    def open(self):
        handle = kernel32.CreateFileW(self.path, GENERIC_READ | GENERIC_WRITE,
                                      3, None, OPEN_EXISTING, 0, None)
        if handle == INVALID_HANDLE_VALUE or handle is None:
            raise UsbError(f"HID-Geraet nicht offen: {self.path}")
        self.handle = handle
        return self

    def write(self, report):
        if self.handle is None:
            raise UsbError("HID-Geraet nicht geoeffnet")
        data = bytes(report)
        buffer = ctypes.create_string_buffer(data, len(data))
        written = wintypes.DWORD()
        if not kernel32.WriteFile(self.handle, buffer, len(data),
                                  ctypes.byref(written), None):
            raise UsbError("HID WriteFile fehlgeschlagen")
        return int(written.value)

    def read(self, size=64):
        if self.handle is None:
            raise UsbError("HID-Geraet nicht geoeffnet")
        buffer = ctypes.create_string_buffer(int(size))
        read = wintypes.DWORD()
        if not kernel32.ReadFile(self.handle, buffer, int(size),
                                 ctypes.byref(read), None):
            raise UsbError("HID ReadFile fehlgeschlagen")
        return buffer.raw[:read.value]

    def close(self):
        if self.handle is not None:
            kernel32.CloseHandle(self.handle)
            self.handle = None
        return self

    def __enter__(self):
        return self.open()

    def __exit__(self, *_exc):
        self.close()
