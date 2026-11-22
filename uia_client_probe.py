"""Minimal IUIAutomation client probe (ctypes COM)."""

from __future__ import annotations

import ctypes
import sys
from ctypes import POINTER, byref, c_int, c_long, c_ulong, c_void_p, wintypes

sys.path.insert(0, r"D:\AI_Temp\AMFWX")

from amfwx.uia_provider import GUID

CLSID_CUIAUTOMATION = GUID.parse("ff48dba4-60ef-4201-aa87-54103eef594e")
IID_IUIAUTOMATION = GUID.parse("30cbe57d-d9d0-452a-ab13-7ac5ac4825ee")

ole32 = ctypes.WinDLL("ole32")
oleaut32 = ctypes.WinDLL("oleaut32")
ole32.CoInitializeEx.argtypes = [c_void_p, c_ulong]
ole32.CoInitializeEx.restype = c_long
ole32.CoCreateInstance.argtypes = [POINTER(GUID), c_void_p, c_ulong,
                                   POINTER(GUID), POINTER(c_void_p)]
ole32.CoCreateInstance.restype = c_long
ole32.CoUninitialize.argtypes = []
oleaut32.SysFreeString.argtypes = [c_void_p]


def vtable(this):
    return ctypes.cast(this, POINTER(POINTER(c_void_p))).contents


def method(this, index, restype, *argtypes):
    address = vtable(this)[index]
    prototype = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)
    return prototype(address)


def bstr(value):
    return ctypes.cast(value, ctypes.c_wchar_p).value if value else ""


def main(hwnd):
    code = ole32.CoInitializeEx(None, 2)
    print("CoInitializeEx", code)
    try:
        automation = c_void_p()
        hr = ole32.CoCreateInstance(byref(CLSID_CUIAUTOMATION), None, 1,
                                    byref(IID_IUIAUTOMATION),
                                    byref(automation))
        print("CoCreateInstance", hex(hr & 0xFFFFFFFF), automation.value)
        if not automation.value:
            return 1
        root = c_void_p()
        get_root = method(automation, 5, c_long, POINTER(c_void_p))
        print('GetRootElement', hex(get_root(automation, byref(root)) & 0xFFFFFFFF), root.value)
        try:
            sent = ctypes.windll.user32.SendMessageW(c_void_p(hwnd), 0x003D,
                                                     -25, 0)
            print('SendMessage WM_GETOBJECT', sent, flush=True)
        except Exception as error:
            print('SendMessage error', error, flush=True)
        element = c_void_p()
        element_from_handle = method(automation, 6, c_long, c_void_p,
                                     POINTER(c_void_p))
        hr = element_from_handle(automation, c_void_p(hwnd),
                                 byref(element))
        print("ElementFromHandle", hex(hr & 0xFFFFFFFF), element.value)
        if not element.value:
            return 1
        try:
            rect = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(c_void_p(hwnd), byref(rect))
            from ctypes import c_long as _long

            class POINT(ctypes.Structure):
                _fields_ = [('x', _long), ('y', _long)]

            point = POINT((rect.left + rect.right) // 2,
                          (rect.top + rect.bottom) // 2)
            at = c_void_p()
            element_from_point = method(automation, 7, c_long, POINT,
                                        POINTER(c_void_p))
            print('ElementFromPoint', hex(element_from_point(automation, point,
                                                              byref(at)) & 0xFFFFFFFF),
                  at.value, flush=True)
            if at.value:
                at_name = c_void_p()
                method(at, 23, c_long, POINTER(c_void_p))(at, byref(at_name))
                at_type = c_int()
                method(at, 21, c_long, POINTER(c_int))(at, byref(at_type))
                print(' point element', bstr(at_name.value), at_type.value,
                      flush=True)
        except Exception as error:
            print('point error', error, flush=True)
        name = c_void_p()
        get_name = method(element, 23, c_long, POINTER(c_void_p))
        hr = get_name(element, byref(name))
        print("CurrentName", hex(hr & 0xFFFFFFFF), bstr(name.value))
        control_type = c_int()
        get_type = method(element, 21, c_long, POINTER(c_int))
        hr = get_type(element, byref(control_type))
        print("ControlType", hex(hr & 0xFFFFFFFF), control_type.value)
        condition = c_void_p()
        create_true = method(automation, 21, c_long, POINTER(c_void_p))
        hr = create_true(automation, byref(condition))
        print("CreateTrueCondition", hex(hr & 0xFFFFFFFF), condition.value)
        children = c_void_p()
        find_all = method(element, 6, c_long, c_int, c_void_p,
                          POINTER(c_void_p))
        hr = find_all(element, 2, condition, byref(children))  # Children
        print("FindAll", hex(hr & 0xFFFFFFFF), children.value)
        if children.value:
            length = c_int()
            get_length = method(children, 3, c_long, POINTER(c_int))
            get_length(children, byref(length))
            print("Children count", length.value)
            for index in range(length.value):
                child = c_void_p()
                get_element = method(children, 4, c_long, c_int,
                                     POINTER(c_void_p))
                get_element(children, index, byref(child))
                child_name = c_void_p()
                method(child, 23, c_long, POINTER(c_void_p))(child,
                                                            byref(child_name))
                child_type = c_int()
                method(child, 21, c_long, POINTER(c_int))(child,
                                                         byref(child_type))
                print(" child", index, bstr(child_name.value),
                      child_type.value)
    finally:
        ole32.CoUninitialize()
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'shell':
            hwnd = ctypes.windll.user32.GetShellWindow()
            print('shell hwnd', hwnd, flush=True)
            raise SystemExit(main(hwnd))
        raise SystemExit(main(int(sys.argv[1])))
    import threading
    from pathlib import Path
    from amfwx import Button, Label, TextEdit, Window

    window = Window("IUIAutomation Probe", 420, 260)
    window.root.add(Label("Probe"))
    window.root.add(Button("Aktion"))
    window.root.add(TextEdit("Text"))
    window.enable_uia()
    Path("D:/AI_Temp/AMFWX/uia_hwnd.txt").write_text(str(window.hwnd))
    threading.Thread(target=main, args=(window.hwnd,), daemon=True).start()
    window.run()
