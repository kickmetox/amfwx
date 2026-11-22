"""Minimal MSAA IAccessible bridge for AMFWX."""

from __future__ import annotations

import ctypes
import uuid
from ctypes import POINTER, byref, c_int, c_long, c_uint, c_ulong, c_void_p
from ctypes import wintypes

from .uia_provider import GUID, oleaut32

IID_IACCESSIBLE = GUID.parse("618736e0-3c3d-11cf-810c-00aa00389b71")
IID_IDISPATCH = GUID.parse("00020400-0000-0000-c000-000000000046")
IID_IUNKNOWN = GUID.parse("00000000-0000-0000-c000-000000000046")

VT_EMPTY = 0
VT_I4 = 3
VT_BSTR = 8
VT_DISPATCH = 9

ROLE_SYSTEM_WINDOW = 0x00000009
ROLE_SYSTEM_PUSHBUTTON = 0x0000002B
ROLE_SYSTEM_TEXT = 0x0000002A
ROLE_SYSTEM_CLIENT = 0x0000000A
ROLE_SYSTEM_CHECKBUTTON = 0x0000002C
ROLE_SYSTEM_LINK = 0x0000001E

STATE_SYSTEM_FOCUSABLE = 0x00100000
STATE_SYSTEM_FOCUSED = 0x00000004
STATE_SYSTEM_OFFSCREEN = 0x00010000
STATE_SYSTEM_INVISIBLE = 0x00008000
STATE_SYSTEM_UNAVAILABLE = 0x00000001

NAVDIR_FIRSTCHILD = 7
NAVDIR_LASTCHILD = 8
NAVDIR_NEXT = 5
NAVDIR_PREVIOUS = 6

CHILDID_SELF = 0


class VARIANT(ctypes.Structure):
    _fields_ = [("vt", ctypes.c_ushort), ("r1", ctypes.c_ushort),
                ("r2", ctypes.c_ushort), ("r3", ctypes.c_ushort),
                ("value", ctypes.c_longlong), ("value2", ctypes.c_longlong)]


def _variant_int(value):
    result = VARIANT()
    result.vt = VT_I4
    result.value = int(value)
    return result


def _variant_empty():
    return VARIANT()


def _variant_string(text):
    result = VARIANT()
    result.vt = VT_BSTR
    bstr = oleaut32.SysAllocString(str(text))
    result.value = ctypes.cast(bstr, c_void_p).value or 0
    return result


def _string(result, text):
    result[0] = ctypes.cast(oleaut32.SysAllocString(str(text)), c_void_p)
    return 0


def _child_index(variant):
    if variant.vt != VT_I4:
        return 0
    return int(variant.value)


class Accessible:
    def __init__(self, window):
        self.window = window
        self.refs = 1
        self._callbacks = []
        self._vtables = []
        self._cells = {}
        self._build()

    def _method(self, restype, *argtypes):
        prototype = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)

        def decorator(function):
            callback = prototype(function)
            self._callbacks.append(callback)
            return ctypes.cast(callback, c_void_p)

        return decorator

    def _build(self):
        qi = self._method(c_long, POINTER(GUID), POINTER(c_void_p))(self._query)
        add = self._method(c_ulong)(self._addref)
        release = self._method(c_ulong)(self._release)
        # IDispatch stubs
        get_type_info_count = self._method(c_long, POINTER(c_uint))(self._type_count)
        get_type_info = self._method(c_long, c_uint, c_uint, POINTER(c_void_p))(self._type_info)
        get_ids = self._method(c_long, c_void_p, c_void_p, c_uint, c_uint,
                                c_void_p)(self._ids)
        invoke = self._method(c_long, c_int, POINTER(GUID), c_uint,
                              ctypes.c_ushort, c_void_p, c_void_p, c_void_p,
                              c_void_p)(self._invoke)
        functions = [
            qi, add, release, get_type_info_count, get_type_info, get_ids,
            invoke,
            self._method(c_long, POINTER(c_void_p))(self._parent),
            self._method(c_long, POINTER(c_long))(self._child_count),
            self._method(c_long, VARIANT, POINTER(c_void_p))(self._child),
            self._method(c_long, VARIANT, POINTER(c_void_p))(self._name),
            self._method(c_long, VARIANT, POINTER(c_void_p))(self._value),
            self._method(c_long, VARIANT, POINTER(c_void_p))(self._description),
            self._method(c_long, VARIANT, POINTER(VARIANT))(self._role),
            self._method(c_long, VARIANT, POINTER(VARIANT))(self._state),
            self._method(c_long, VARIANT, POINTER(c_void_p))(self._help),
            self._method(c_long, POINTER(c_void_p), VARIANT,
                         POINTER(c_long))(self._help_topic),
            self._method(c_long, VARIANT, POINTER(c_void_p))(self._shortcut),
            self._method(c_long, POINTER(VARIANT))(self._focus),
            self._method(c_long, POINTER(VARIANT))(self._selection),
            self._method(c_long, VARIANT, POINTER(c_void_p))(self._default_action),
            self._method(c_long, c_long, VARIANT)(self._select),
            self._method(c_long, POINTER(c_long), POINTER(c_long),
                         POINTER(c_long), POINTER(c_long),
                         VARIANT)(self._location),
            self._method(c_long, c_long, VARIANT,
                         POINTER(VARIANT))(self._navigate),
            self._method(c_long, c_long, c_long,
                         POINTER(VARIANT))(self._hit_test),
            self._method(c_long, VARIANT)(self._do_default),
            self._method(c_long, VARIANT, c_void_p)(self._put_name),
            self._method(c_long, VARIANT, c_void_p)(self._put_value),
        ]
        array = (c_void_p * len(functions))(*functions)
        self._vtables.append(array)
        holder = c_void_p(ctypes.addressof(array))
        self._vtables.append(holder)
        self._interface = c_void_p(ctypes.addressof(holder))
        self._cells["accessible"] = self._interface
        _objects[self._interface.value] = self

    def _query(self, this, riid, result):
        try:
            value = ctypes.cast(riid, POINTER(GUID)).contents
            target = str(uuid.UUID(bytes_le=(
                value.Data1.to_bytes(4, "little") +
                value.Data2.to_bytes(2, "little") +
                value.Data3.to_bytes(2, "little") +
                bytes(value.Data4))))
        except Exception:
            target = ""
        if target in (str(IID_IACCESSIBLE), str(IID_IDISPATCH),
                      str(IID_IUNKNOWN)):
            self.refs += 1
            result[0] = self._interface
            return 0
        return -2147467262

    def _addref(self, this):
        self.refs += 1
        return self.refs

    def _release(self, this):
        self.refs -= 1
        return self.refs

    # IDispatch
    def _type_count(self, this, result):
        result[0] = 0
        return 0

    def _type_info(self, this, index, locale, result):
        result[0] = None
        return -2147467263

    def _ids(self, this, names, locale, count, names_ptr, result):
        return -2147467263

    def _invoke(self, this, member, iid, locale, flags, params, result,
                exception, argument_error):
        return -2147467263

    def _widgets(self):
        result = []
        stack = list(reversed(getattr(self.window.root, "children", [])))
        while stack:
            widget = stack.pop()
            result.append(widget)
            stack.extend(reversed(getattr(widget, "children", [])))
        return result

    def _widget(self, child_id):
        widgets = self._widgets()
        index = int(child_id) - 1
        return widgets[index] if 0 <= index < len(widgets) else None

    def _text(self, widget):
        value = getattr(widget, "text", "")
        if callable(value):
            value = value()
        return str(value or "")

    # IAccessible
    def _parent(self, this, result):
        result[0] = None
        return 0

    def _child_count(self, this, result):
        result[0] = len(self._widgets())
        return 0

    def _child(self, this, child, result):
        result[0] = None
        return 1  # S_FALSE for virtual children

    def _name(self, this, child, result):
        child_id = _child_index(child)
        if child_id == CHILDID_SELF:
            return _string(result, self.window.title)
        widget = self._widget(child_id)
        if widget is None:
            return _string(result, "")
        return _string(result, self._text(widget))

    def _value(self, this, child, result):
        child_id = _child_index(child)
        widget = self._widget(child_id) if child_id else None
        if widget is None:
            return _string(result, "")
        return _string(result, self._text(widget))

    def _description(self, this, child, result):
        return _string(result, "")

    def _role(self, this, child, result):
        child_id = _child_index(child)
        if child_id == CHILDID_SELF:
            result[0] = _variant_int(ROLE_SYSTEM_WINDOW)
            return 0
        widget = self._widget(child_id)
        name = type(widget).__name__ if widget is not None else ""
        roles = {"Button": ROLE_SYSTEM_PUSHBUTTON,
                 "CheckBox": ROLE_SYSTEM_CHECKBUTTON,
                 "Label": ROLE_SYSTEM_TEXT,
                 "LineEdit": ROLE_SYSTEM_TEXT,
                 "TextEdit": ROLE_SYSTEM_TEXT}
        result[0] = _variant_int(roles.get(name, ROLE_SYSTEM_CLIENT))
        return 0

    def _state(self, this, child, result):
        child_id = _child_index(child)
        widget = self._widget(child_id) if child_id else None
        state = 0
        if widget is not None:
            state |= STATE_SYSTEM_FOCUSABLE
            if getattr(widget, "focused", False):
                state |= STATE_SYSTEM_FOCUSED
            if not getattr(widget, "enabled", True):
                state |= STATE_SYSTEM_UNAVAILABLE
            if getattr(widget, "rect", None) is None:
                state |= STATE_SYSTEM_INVISIBLE
        result[0] = _variant_int(state)
        return 0

    def _help(self, this, child, result):
        return _string(result, "")

    def _help_topic(self, this, help_file, child, result):
        result[0] = -1
        return 0

    def _shortcut(self, this, child, result):
        return _string(result, "")

    def _focus(self, this, result):
        result[0] = _variant_empty()
        return 0

    def _selection(self, this, result):
        result[0] = _variant_empty()
        return 0

    def _default_action(self, this, child, result):
        child_id = _child_index(child)
        widget = self._widget(child_id) if child_id else None
        return _string(result, "Drücken" if widget is not None else "")

    def _select(self, this, flags, child):
        return 0

    def _location(self, this, left, top, width, height, child):
        child_id = _child_index(child)
        widget = self.window.root if child_id == CHILDID_SELF else self._widget(child_id)
        rect = getattr(widget, "rect", None)
        if rect is None:
            left[0] = top[0] = width[0] = height[0] = 0
            return 0
        point = wintypes.POINT(0, 0)
        ctypes.windll.user32.ClientToScreen(
            ctypes.c_void_p(self.window.hwnd), byref(point))
        left[0] = point.x + rect.x
        top[0] = point.y + rect.y
        width[0] = rect.w
        height[0] = rect.h
        return 0

    def _navigate(self, this, direction, start, result):
        child_id = _child_index(start)
        widgets = self._widgets()
        target = 0
        if direction == NAVDIR_FIRSTCHILD:
            target = 1
        elif direction == NAVDIR_LASTCHILD:
            target = len(widgets)
        elif direction == NAVDIR_NEXT and child_id < len(widgets):
            target = child_id + 1
        elif direction == NAVDIR_PREVIOUS and child_id > 1:
            target = child_id - 1
        result[0] = _variant_int(target) if target else _variant_empty()
        return 0

    def _hit_test(self, this, x, y, result):
        widget = self.window._widget_at(x, y)
        widgets = self._widgets()
        result[0] = _variant_int(widgets.index(widget) + 1
                                 if widget in widgets else CHILDID_SELF)
        return 0

    def _do_default(self, this, child):
        child_id = _child_index(child)
        widget = self._widget(child_id) if child_id else None
        if widget is not None and hasattr(widget, "activate"):
            widget.activate()
        return 0

    def _put_name(self, this, child, name):
        return 0

    def _put_value(self, this, child, value):
        return 0


_objects = {}


def lresult(accessible, wparam):
    import ctypes
    oleacc = ctypes.WinDLL("oleacc")
    oleacc.LresultFromObject.argtypes = [POINTER(GUID), ctypes.c_size_t,
                                         c_void_p]
    oleacc.LresultFromObject.restype = ctypes.c_ssize_t
    return oleacc.LresultFromObject(byref(IID_IACCESSIBLE), wparam,
                                    accessible._interface)


OBJID_CLIENT = -4


def _oleacc():
    import ctypes
    return ctypes.windll.oleacc


def read_accessible(hwnd):
    """Read name and role from the native MSAA provider of a window."""
    import ctypes
    from ctypes import POINTER, byref, c_long, c_ulong, c_void_p
    import ctypes.wintypes as wt
    oleacc = _oleacc()
    oleacc.AccessibleObjectFromWindow.argtypes = [
        c_void_p, wt.DWORD, POINTER(GUID), POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    pointer = c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        c_void_p(int(hwnd)), ctypes.c_ulong(OBJID_CLIENT & 0xFFFFFFFF),
        byref(IID_IACCESSIBLE), byref(pointer))
    if hr != 0 or not pointer:
        return {"error": hr}
    vtable = ctypes.cast(pointer, POINTER(POINTER(c_void_p))).contents
    child = VARIANT()
    name_pointer = c_void_p()
    get_name = ctypes.WINFUNCTYPE(c_long, c_void_p, VARIANT,
                                  POINTER(c_void_p))(vtable[10])
    get_value = ctypes.WINFUNCTYPE(c_long, c_void_p, VARIANT,
                                   POINTER(c_void_p))(vtable[11])
    get_role = ctypes.WINFUNCTYPE(c_long, c_void_p, VARIANT,
                                  POINTER(VARIANT))(vtable[13])
    get_state = ctypes.WINFUNCTYPE(c_long, c_void_p, VARIANT,
                                   POINTER(VARIANT))(vtable[14])
    name_hr = get_name(pointer, child, byref(name_pointer))
    name = ""
    if name_hr == 0 and name_pointer.value:
        name = ctypes.wstring_at(name_pointer.value)
        oleaut32.SysFreeString(name_pointer)
    value_pointer = c_void_p()
    value_hr = get_value(pointer, child, byref(value_pointer))
    value = ""
    if value_hr == 0 and value_pointer.value:
        value = ctypes.wstring_at(value_pointer.value)
        oleaut32.SysFreeString(value_pointer)
    role = VARIANT()
    role_hr = get_role(pointer, child, byref(role))
    state = VARIANT()
    state_hr = get_state(pointer, child, byref(state))
    release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])
    release(pointer)
    return {"name": name, "value": value,
            "role": role.value if role_hr == 0 else None,
            "state": state.value if state_hr == 0 else None,
            "name_hr": name_hr, "value_hr": value_hr,
            "role_hr": role_hr, "state_hr": state_hr}


def do_default_action(hwnd):
    """Invoke the native MSAA default action of a window."""
    import ctypes
    from ctypes import POINTER, byref, c_long, c_ulong, c_void_p
    import ctypes.wintypes as wt
    oleacc = _oleacc()
    oleacc.AccessibleObjectFromWindow.argtypes = [
        c_void_p, wt.DWORD, POINTER(GUID), POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    pointer = c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        c_void_p(int(hwnd)), ctypes.c_ulong(OBJID_CLIENT & 0xFFFFFFFF),
        byref(IID_IACCESSIBLE), byref(pointer))
    if hr != 0 or not pointer:
        return hr
    vtable = ctypes.cast(pointer, POINTER(POINTER(c_void_p))).contents
    child = VARIANT()
    action = ctypes.WINFUNCTYPE(c_long, c_void_p, VARIANT)(vtable[25])
    result = action(pointer, child)
    release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])
    release(pointer)
    return result


def set_accessible_value(hwnd, text):
    """Set a native MSAA value (for example an edit proxy)."""
    import ctypes
    from ctypes import POINTER, byref, c_long, c_ulong, c_void_p
    import ctypes.wintypes as wt
    oleacc = _oleacc()
    oleacc.AccessibleObjectFromWindow.argtypes = [
        c_void_p, wt.DWORD, POINTER(GUID), POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    pointer = c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        c_void_p(int(hwnd)), ctypes.c_ulong(OBJID_CLIENT & 0xFFFFFFFF),
        byref(IID_IACCESSIBLE), byref(pointer))
    if hr != 0 or not pointer:
        return hr
    vtable = ctypes.cast(pointer, POINTER(POINTER(c_void_p))).contents
    child = VARIANT()
    bstr = oleaut32.SysAllocString(str(text))
    put_value = ctypes.WINFUNCTYPE(c_long, c_void_p, VARIANT,
                                   c_void_p)(vtable[27])
    result = put_value(pointer, child, ctypes.cast(bstr, c_void_p))
    oleaut32.SysFreeString(ctypes.cast(bstr, c_void_p))
    release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])
    release(pointer)
    return result


def select_accessible(hwnd, flags=1):
    """Call IAccessible::accSelect (1 = take focus)."""
    import ctypes
    from ctypes import POINTER, byref, c_long, c_ulong, c_void_p
    import ctypes.wintypes as wt
    oleacc = _oleacc()
    oleacc.AccessibleObjectFromWindow.argtypes = [
        c_void_p, wt.DWORD, POINTER(GUID), POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    pointer = c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        c_void_p(int(hwnd)), ctypes.c_ulong(OBJID_CLIENT & 0xFFFFFFFF),
        byref(IID_IACCESSIBLE), byref(pointer))
    if hr != 0 or not pointer:
        return hr
    vtable = ctypes.cast(pointer, POINTER(POINTER(c_void_p))).contents
    child = VARIANT()
    select = ctypes.WINFUNCTYPE(c_long, c_void_p, c_long, VARIANT)(vtable[21])
    result = select(pointer, int(flags), child)
    try:
        ctypes.windll.user32.SetFocus(c_void_p(int(hwnd)))
    except Exception:
        pass
    release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])
    release(pointer)
    return result


def read_focus(hwnd):
    """Return the MSAA focus VARIANT type and value for a window."""
    import ctypes
    from ctypes import POINTER, byref, c_long, c_ulong, c_void_p
    import ctypes.wintypes as wt
    oleacc = _oleacc()
    oleacc.AccessibleObjectFromWindow.argtypes = [
        c_void_p, wt.DWORD, POINTER(GUID), POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    pointer = c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        c_void_p(int(hwnd)), ctypes.c_ulong(OBJID_CLIENT & 0xFFFFFFFF),
        byref(IID_IACCESSIBLE), byref(pointer))
    if hr != 0 or not pointer:
        return {"error": hr}
    vtable = ctypes.cast(pointer, POINTER(POINTER(c_void_p))).contents
    result = VARIANT()
    get_focus = ctypes.WINFUNCTYPE(c_long, c_void_p,
                                   POINTER(VARIANT))(vtable[18])
    focus_hr = get_focus(pointer, byref(result))
    release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])
    release(pointer)
    return {"hr": focus_hr, "vt": result.vt, "value": result.value}


def read_selection(hwnd):
    """Return the MSAA selection VARIANT for a window."""
    import ctypes
    from ctypes import POINTER, byref, c_long, c_ulong, c_void_p
    import ctypes.wintypes as wt
    oleacc = _oleacc()
    oleacc.AccessibleObjectFromWindow.argtypes = [
        c_void_p, wt.DWORD, POINTER(GUID), POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    pointer = c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        c_void_p(int(hwnd)), ctypes.c_ulong(OBJID_CLIENT & 0xFFFFFFFF),
        byref(IID_IACCESSIBLE), byref(pointer))
    if hr != 0 or not pointer:
        return {"error": hr}
    vtable = ctypes.cast(pointer, POINTER(POINTER(c_void_p))).contents
    result = VARIANT()
    get_selection = ctypes.WINFUNCTYPE(c_long, c_void_p,
                                       POINTER(VARIANT))(vtable[19])
    selection_hr = get_selection(pointer, byref(result))
    release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])
    release(pointer)
    return {"hr": selection_hr, "vt": result.vt, "value": result.value}


def read_location(hwnd):
    """Return the MSAA screen rectangle of a window."""
    import ctypes
    from ctypes import POINTER, byref, c_long, c_ulong, c_void_p
    import ctypes.wintypes as wt
    oleacc = _oleacc()
    oleacc.AccessibleObjectFromWindow.argtypes = [
        c_void_p, wt.DWORD, POINTER(GUID), POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    pointer = c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        c_void_p(int(hwnd)), ctypes.c_ulong(OBJID_CLIENT & 0xFFFFFFFF),
        byref(IID_IACCESSIBLE), byref(pointer))
    if hr != 0 or not pointer:
        return {"error": hr}
    vtable = ctypes.cast(pointer, POINTER(POINTER(c_void_p))).contents
    x = c_long()
    y = c_long()
    width = c_long()
    height = c_long()
    child = VARIANT()
    location = ctypes.WINFUNCTYPE(
        c_long, c_void_p, POINTER(c_long), POINTER(c_long),
        POINTER(c_long), POINTER(c_long), VARIANT)(vtable[22])
    location_hr = location(pointer, byref(x), byref(y), byref(width),
                           byref(height), child)
    release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])
    release(pointer)
    return {"hr": location_hr, "x": x.value, "y": y.value,
            "width": width.value, "height": height.value}


def set_accessible_name(hwnd, text):
    """Set the MSAA accessible name of a window (put_accName)."""
    import ctypes
    from ctypes import POINTER, byref, c_long, c_ulong, c_void_p
    import ctypes.wintypes as wt
    oleacc = _oleacc()
    oleacc.AccessibleObjectFromWindow.argtypes = [
        c_void_p, wt.DWORD, POINTER(GUID), POINTER(c_void_p)]
    oleacc.AccessibleObjectFromWindow.restype = c_long
    pointer = c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        c_void_p(int(hwnd)), ctypes.c_ulong(OBJID_CLIENT & 0xFFFFFFFF),
        byref(IID_IACCESSIBLE), byref(pointer))
    if hr != 0 or not pointer:
        return hr
    vtable = ctypes.cast(pointer, POINTER(POINTER(c_void_p))).contents
    child = VARIANT()
    bstr = oleaut32.SysAllocString(str(text))
    put_name = ctypes.WINFUNCTYPE(c_long, c_void_p, VARIANT,
                                  c_void_p)(vtable[26])
    result = put_name(pointer, child, ctypes.cast(bstr, c_void_p))
    oleaut32.SysFreeString(ctypes.cast(bstr, c_void_p))
    release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])
    release(pointer)
    return result
