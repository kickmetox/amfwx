"""Minimal MSAA IAccessible client probe."""

from __future__ import annotations

import ctypes
import sys
from ctypes import POINTER, byref, c_int, c_long, c_void_p, wintypes

from amfwx.msaa import IID_IACCESSIBLE, VARIANT


def method(this, index, restype, *argtypes):
    table = ctypes.cast(this, POINTER(POINTER(c_void_p))).contents
    prototype = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)
    return prototype(table[index])


def main(hwnd):
    oleacc = ctypes.WinDLL("oleacc")
    oleacc.AccessibleObjectFromWindow.argtypes = [c_void_p, ctypes.c_ulong,
                                                  POINTER(type(IID_IACCESSIBLE)),
                                                  POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    ctypes.windll.user32.SendMessageW(c_void_p(hwnd), 0x003D, 0xFFFFFFFC, 0)
    accessible = c_void_p()
    code = oleacc.AccessibleObjectFromWindow(
        c_void_p(hwnd), 0xFFFFFFFC, byref(IID_IACCESSIBLE),
        byref(accessible))
    print("AccessibleObjectFromWindow", hex(code & 0xFFFFFFFF),
          accessible.value, flush=True)
    if not accessible.value:
        return 1
    count = c_int()
    get_count = method(accessible, 8, c_long, POINTER(c_int))
    get_count(accessible, byref(count))
    print("childCount", count.value, flush=True)
    for index in range(1, count.value + 1):
        child = VARIANT()
        child.vt = 3
        child.value = index
        name = c_void_p()
        method(accessible, 10, c_long, VARIANT,
               POINTER(c_void_p))(accessible, child, byref(name))
        role = VARIANT()
        method(accessible, 13, c_long, VARIANT,
               POINTER(VARIANT))(accessible, child, byref(role))
        print(" child", index,
              ctypes.wstring_at(name.value) if name.value else "",
              role.value, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1])))
