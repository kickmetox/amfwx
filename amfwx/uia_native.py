"""Native UIA provider binding for AMFWX proxy windows."""

from __future__ import annotations

import ctypes
import os


ROLE_BUTTON = 0
ROLE_CHECKBOX = 1
ROLE_EDIT = 2
ROLE_TEXT = 3
ROLE_PANE = 4


def _library():
    path = os.path.join(os.path.dirname(__file__), "bin", "uia_provider.dll")
    library = ctypes.WinDLL(path)
    library.amfwx_uia_attach.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                         ctypes.c_wchar_p, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int]
    library.amfwx_uia_attach.restype = ctypes.c_int
    library.amfwx_uia_set_name.argtypes = [ctypes.c_void_p,
                                           ctypes.c_wchar_p]
    library.amfwx_uia_set_name.restype = ctypes.c_int
    library.amfwx_uia_set_bounds.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int,
                                             ctypes.c_int]
    library.amfwx_uia_set_bounds.restype = ctypes.c_int
    library.amfwx_uia_notify_focus.argtypes = [ctypes.c_void_p]
    library.amfwx_uia_notify_structure.argtypes = [ctypes.c_void_p]
    library.amfwx_uia_notify_structure.restype = ctypes.c_int
    library.amfwx_uia_notify_name.argtypes = [ctypes.c_void_p,
                                             ctypes.c_wchar_p,
                                             ctypes.c_wchar_p]
    library.amfwx_uia_notify_name.restype = ctypes.c_int
    library.amfwx_uia_notify_focus.restype = ctypes.c_int
    library.amfwx_uia_detach.argtypes = [ctypes.c_void_p]
    library.amfwx_uia_detach.restype = ctypes.c_int
    return library


def role_for_widget(widget):
    name = type(widget).__name__
    if name == "Button":
        return ROLE_BUTTON
    if name == "CheckBox":
        return ROLE_CHECKBOX
    if name in ("LineEdit", "TextEdit"):
        return ROLE_EDIT
    if name in ("Label", "Static"):
        return ROLE_TEXT
    return ROLE_PANE


def attach(hwnd, widget, name="", control_id=0, x=0, y=0, width=1, height=1):
    return _library().amfwx_uia_attach(
        ctypes.c_void_p(int(hwnd)), role_for_widget(widget),
        str(name or ""), int(control_id), int(x), int(y),
        int(width), int(height))


def set_name(hwnd, name):
    return _library().amfwx_uia_set_name(
        ctypes.c_void_p(int(hwnd)), str(name or ""))


def set_bounds(hwnd, x, y, width, height):
    return _library().amfwx_uia_set_bounds(
        ctypes.c_void_p(int(hwnd)), int(x), int(y), int(width), int(height))


def notify_structure(hwnd):
    return _library().amfwx_uia_notify_structure(ctypes.c_void_p(int(hwnd)))


def notify_name(hwnd, old_name="", new_name=""):
    return _library().amfwx_uia_notify_name(
        ctypes.c_void_p(int(hwnd)), str(old_name or ""),
        str(new_name or ""))


def notify_focus(hwnd):
    return _library().amfwx_uia_notify_focus(ctypes.c_void_p(int(hwnd)))


def detach(hwnd):
    return _library().amfwx_uia_detach(ctypes.c_void_p(int(hwnd)))
