"""Raw USB devices via WinUSB."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


DIGCF_PRESENT = 0x00000002
DIGCF_DEVICEINTERFACE = 0x00000010
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
USB_DEVICE_DESCRIPTOR_TYPE = 0x01


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]


class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD),
                ("InterfaceClassGuid", GUID),
                ("Flags", wintypes.DWORD),
                ("Reserved", ctypes.c_void_p)]


class USB_DEVICE_DESCRIPTOR(ctypes.Structure):
    _fields_ = [("bLength", ctypes.c_ubyte),
                ("bDescriptorType", ctypes.c_ubyte),
                ("bcdUSB", wintypes.WORD),
                ("bDeviceClass", ctypes.c_ubyte),
                ("bDeviceSubClass", ctypes.c_ubyte),
                ("bDeviceProtocol", ctypes.c_ubyte),
                ("bMaxPacketSize0", ctypes.c_ubyte),
                ("idVendor", wintypes.WORD),
                ("idProduct", wintypes.WORD),
                ("bcdDevice", wintypes.WORD),
                ("iManufacturer", ctypes.c_ubyte),
                ("iProduct", ctypes.c_ubyte),
                ("iSerialNumber", ctypes.c_ubyte),
                ("bNumConfigurations", ctypes.c_ubyte)]


USB_GUID = GUID(0xA5DCBF10, 0x6530, 0x11D2,
                (0x90, 0x1F, 0x00, 0xC0, 0x4F, 0xB9, 0x51, 0xED))

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

winusb = ctypes.WinDLL("winusb.dll", use_last_error=True)
winusb.WinUsb_Initialize.argtypes = [wintypes.HANDLE,
                                     ctypes.POINTER(ctypes.c_void_p)]
winusb.WinUsb_Free.argtypes = [ctypes.c_void_p]
winusb.WinUsb_GetDescriptor.argtypes = [ctypes.c_void_p, ctypes.c_ubyte,
                                        ctypes.c_ubyte, wintypes.WORD,
                                        ctypes.c_void_p, wintypes.DWORD,
                                        ctypes.POINTER(wintypes.DWORD)]
winusb.WinUsb_ReadPipe.argtypes = [ctypes.c_void_p, ctypes.c_ubyte,
                                   ctypes.c_void_p, wintypes.DWORD,
                                   ctypes.POINTER(wintypes.DWORD),
                                   ctypes.c_void_p]
winusb.WinUsb_WritePipe.argtypes = [ctypes.c_void_p, ctypes.c_ubyte,
                                    ctypes.c_void_p, wintypes.DWORD,
                                    ctypes.POINTER(wintypes.DWORD),
                                    ctypes.c_void_p]
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                 wintypes.DWORD, ctypes.c_void_p,
                                 wintypes.DWORD, wintypes.DWORD,
                                 wintypes.HANDLE]
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


class UsbRawError(RuntimeError):
    pass


class UsbDeviceInfo:
    def __init__(self, path, vendor_id, product_id, device_class):
        self.path = path
        self.vendor_id = int(vendor_id)
        self.product_id = int(product_id)
        self.device_class = int(device_class)

    def __repr__(self):
        return (f"UsbDeviceInfo({self.vendor_id:04X}:{self.product_id:04X})")


def _details(handle, interface):
    required = wintypes.DWORD()
    setupapi.SetupDiGetDeviceInterfaceDetailW(
        handle, ctypes.byref(interface), None, 0, ctypes.byref(required), None)
    if not required.value:
        return None
    buffer = ctypes.create_string_buffer(required.value)
    detail = ctypes.cast(buffer, ctypes.POINTER(
        wintypes.DWORD))
    detail.contents.value = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
    if not setupapi.SetupDiGetDeviceInterfaceDetailW(
            handle, ctypes.byref(interface), buffer, required.value,
            ctypes.byref(required), None):
        return None
    return ctypes.wstring_at(ctypes.addressof(buffer) + 4)


def list_usb_devices():
    handle = setupapi.SetupDiGetClassDevsW(ctypes.byref(USB_GUID), None, None,
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
                    handle, None, ctypes.byref(USB_GUID), index,
                    ctypes.byref(interface)):
                break
            index += 1
            path = _details(handle, interface)
            if not path:
                continue
            file_handle = kernel32.CreateFileW(path, GENERIC_READ | GENERIC_WRITE,
                                               3, None, OPEN_EXISTING, 0, None)
            if file_handle == INVALID_HANDLE_VALUE or file_handle is None:
                continue
            usb_handle = ctypes.c_void_p()
            try:
                if not winusb.WinUsb_Initialize(file_handle,
                                                ctypes.byref(usb_handle)):
                    continue
                descriptor = USB_DEVICE_DESCRIPTOR()
                transferred = wintypes.DWORD()
                if not winusb.WinUsb_GetDescriptor(
                        usb_handle, USB_DEVICE_DESCRIPTOR_TYPE, 0, 0,
                        ctypes.byref(descriptor), ctypes.sizeof(descriptor),
                        ctypes.byref(transferred)):
                    continue
                devices.append(UsbDeviceInfo(
                    path, descriptor.idVendor, descriptor.idProduct,
                    descriptor.bDeviceClass))
            finally:
                if usb_handle:
                    winusb.WinUsb_Free(usb_handle)
                kernel32.CloseHandle(file_handle)
    finally:
        setupapi.SetupDiDestroyDeviceInfoList(handle)
    return devices


class WinUsbDevice:
    def __init__(self, path):
        self.path = str(path)
        self.file_handle = None
        self.usb_handle = None

    def open(self):
        file_handle = kernel32.CreateFileW(
            self.path, GENERIC_READ | GENERIC_WRITE, 3, None, OPEN_EXISTING,
            0, None)
        if file_handle == INVALID_HANDLE_VALUE or file_handle is None:
            raise UsbRawError(f"USB-Geraet nicht offen: {self.path}")
        usb_handle = ctypes.c_void_p()
        if not winusb.WinUsb_Initialize(file_handle,
                                        ctypes.byref(usb_handle)):
            kernel32.CloseHandle(file_handle)
            raise UsbRawError("WinUsb_Initialize fehlgeschlagen")
        self.file_handle = file_handle
        self.usb_handle = usb_handle
        return self

    def write(self, pipe_id, data):
        if self.usb_handle is None:
            raise UsbRawError("USB nicht geoeffnet")
        payload = bytes(data)
        buffer = ctypes.create_string_buffer(payload, len(payload))
        transferred = wintypes.DWORD()
        if not winusb.WinUsb_WritePipe(
                self.usb_handle, int(pipe_id), buffer, len(payload),
                ctypes.byref(transferred), None):
            raise UsbRawError("WinUsb_WritePipe fehlgeschlagen")
        return int(transferred.value)

    def read(self, pipe_id, size=64):
        if self.usb_handle is None:
            raise UsbRawError("USB nicht geoeffnet")
        buffer = ctypes.create_string_buffer(int(size))
        transferred = wintypes.DWORD()
        if not winusb.WinUsb_ReadPipe(
                self.usb_handle, int(pipe_id), buffer, int(size),
                ctypes.byref(transferred), None):
            raise UsbRawError("WinUsb_ReadPipe fehlgeschlagen")
        return buffer.raw[:transferred.value]

    def close(self):
        if self.usb_handle is not None:
            winusb.WinUsb_Free(self.usb_handle)
            self.usb_handle = None
        if self.file_handle is not None:
            kernel32.CloseHandle(self.file_handle)
            self.file_handle = None
        return self

    def __enter__(self):
        return self.open()

    def __exit__(self, *_exc):
        self.close()
