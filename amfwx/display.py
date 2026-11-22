"""Windows display/monitor enumeration and window placement."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


ENUM_CURRENT_SETTINGS = -1
MONITOR_DEFAULTTONEAREST = 2
SWP_SHOWWINDOW = 0x0040
WS_POPUP = 0x80000000
WS_OVERLAPPEDWINDOW = 0x00CF0000


class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]


class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPositionX", wintypes.LONG),
        ("dmPositionY", wintypes.LONG),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]


class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", RECT),
                ("rcWork", RECT), ("dwFlags", wintypes.DWORD)]


user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.EnumDisplayDevicesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                      ctypes.POINTER(DISPLAY_DEVICEW),
                                      wintypes.DWORD]
user32.EnumDisplaySettingsW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                        ctypes.POINTER(DEVMODEW)]
user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_longlong]
user32.SetWindowLongPtrW.restype = ctypes.c_longlong
user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongPtrW.restype = ctypes.c_longlong
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                wintypes.UINT]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.MonitorFromWindow.restype = wintypes.HANDLE
user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]


class Monitor:
    def __init__(self, name, adapter, x, y, width, height, refresh,
                 bits, primary=False, orientation=0):
        self.name = name
        self.adapter = adapter
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.refresh = int(refresh)
        self.bits = int(bits)
        self.primary = bool(primary)
        self.orientation = int(orientation)

    def __repr__(self):
        return (f"Monitor({self.name!r}, {self.width}x{self.height}"
                f"@{self.refresh}, primary={self.primary})")

    def to_dict(self):
        return {"name": self.name, "adapter": self.adapter, "x": self.x,
                "y": self.y, "width": self.width, "height": self.height,
                "refresh": self.refresh, "bits": self.bits,
                "primary": self.primary, "orientation": self.orientation}


def list_monitors():
    monitors = []
    index = 0
    while True:
        device = DISPLAY_DEVICEW()
        device.cb = ctypes.sizeof(DISPLAY_DEVICEW)
        if not user32.EnumDisplayDevicesW(None, index, ctypes.byref(device), 0):
            break
        index += 1
        if not (device.StateFlags & 0x00000001):
            continue
        mode = DEVMODEW()
        mode.dmSize = ctypes.sizeof(DEVMODEW)
        if not user32.EnumDisplaySettingsW(device.DeviceName,
                                           ENUM_CURRENT_SETTINGS,
                                           ctypes.byref(mode)):
            continue
        monitors.append(Monitor(
            name=device.DeviceName, adapter=device.DeviceString,
            x=mode.dmPositionX, y=mode.dmPositionY,
            width=mode.dmPelsWidth, height=mode.dmPelsHeight,
            refresh=mode.dmDisplayFrequency, bits=mode.dmBitsPerPel,
            primary=not monitors,
            orientation=mode.dmDisplayOrientation))
    return monitors


def primary_monitor():
    monitors = list_monitors()
    return monitors[0] if monitors else None


def monitor_work_area(window):
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    handle = user32.MonitorFromWindow(window.hwnd, MONITOR_DEFAULTTONEAREST)
    if user32.GetMonitorInfoW(handle, ctypes.byref(info)):
        return (info.rcWork.left, info.rcWork.top,
                info.rcWork.right - info.rcWork.left,
                info.rcWork.bottom - info.rcWork.top)
    return None


def move_to_monitor(window, monitor, fullscreen=False):
    if fullscreen:
        style = user32.GetWindowLongPtrW(window.hwnd, -16)
        window._display_style = style
        user32.SetWindowLongPtrW(window.hwnd, -16, WS_POPUP | 0x10000000)
        user32.SetWindowPos(window.hwnd, None, monitor.x, monitor.y,
                            monitor.width, monitor.height,
                            SWP_SHOWWINDOW)
    else:
        user32.SetWindowPos(window.hwnd, None, monitor.x + 40,
                            monitor.y + 40, window.width, window.height,
                            SWP_SHOWWINDOW)
    return window


def fullscreen(window, monitor=None):
    monitor = monitor or primary_monitor()
    if monitor is None:
        return window
    window._display_windowed_rect = RECT()
    user32.GetWindowRect(window.hwnd,
                         ctypes.byref(window._display_windowed_rect))
    return move_to_monitor(window, monitor, fullscreen=True)


def exit_fullscreen(window):
    rect = getattr(window, "_display_windowed_rect", None)
    style = getattr(window, "_display_style", WS_OVERLAPPEDWINDOW)
    user32.SetWindowLongPtrW(window.hwnd, -16, style)
    if rect is not None:
        user32.SetWindowPos(window.hwnd, None, rect.left, rect.top,
                            rect.right - rect.left, rect.bottom - rect.top,
                            SWP_SHOWWINDOW)
    return window
