"""UIA TextPattern/SelectionPattern implementation for AMFWX."""

from __future__ import annotations

import ctypes
import uuid
from ctypes import POINTER, byref, c_double, c_int, c_long, c_uint, c_void_p
from ctypes import wintypes

from .uia_provider import (
    GUID, VARIANT, _objects, _variant_string, oleaut32,
)

IID_TEXT = GUID.parse("3589c92c-63f3-4367-99bb-ada653b77cf2")
IID_RANGE = GUID.parse("5347ad7b-c355-46f8-aff5-909033582f63")
UIA_TextPatternId = 10014
SupportedTextSelection_Single = 1
VT_UNKNOWN = 13
VT_R8 = 5


class UiaPoint(ctypes.Structure):
    _fields_ = [("x", c_double), ("y", c_double)]


def _holder(array):
    holder = ctypes.c_void_p(ctypes.addressof(array))
    return ctypes.c_void_p(ctypes.addressof(holder)), holder


def _array(items, vt=VT_UNKNOWN):
    array = oleaut32.SafeArrayCreateVector(vt, 0, len(items))
    for index, item in enumerate(items):
        oleaut32.SafeArrayPutElement(array, byref(c_long(index)),
                                     ctypes.c_void_p(item.value))
    return array


def _double_array(values):
    array = oleaut32.SafeArrayCreateVector(VT_R8, 0, len(values))
    for index, value in enumerate(values):
        item = c_double(value)
        oleaut32.SafeArrayPutElement(array, byref(c_long(index)), byref(item))
    return array


class _TextBase:
    def _method(self, restype, *argtypes):
        prototype = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)

        def decorator(function):
            lock = getattr(self, "_lock", None)

            def guarded(*args):
                import threading
                window = getattr(self, "window", None)
                if window is not None and threading.get_ident() != getattr(window, "ui_thread", None):
                    return window.invoke(lambda: function(*args))
                if lock is None:
                    return function(*args)
                with lock:
                    return function(*args)

            callback = prototype(guarded)
            self._callbacks.append(callback)
            return ctypes.cast(callback, c_void_p)

        return decorator

    def _make(self, name, functions, iid):
        array = (c_void_p * len(functions))(*functions)
        self._vtables.append(array)
        interface, holder = _holder(array)
        self._vtables.append(holder)
        self._cells[name] = interface
        _objects[interface.value] = self
        setattr(self, name, interface)


class TextProvider(_TextBase):
    def __init__(self, provider):
        self.provider = provider
        self.widget = provider.widget
        self.window = provider.window
        self.refs = 1
        import threading
        self._lock = threading.RLock()
        self._callbacks = []
        self._vtables = []
        self._cells = {}
        qi = self._method(c_long, POINTER(GUID), POINTER(c_void_p))(self._query)
        add = self._method(ctypes.c_ulong)(self._addref)
        release = self._method(ctypes.c_ulong)(self._release)
        methods = [
            qi, add, release,
            self._method(c_long, POINTER(c_void_p))(self._selection),
            self._method(c_long, POINTER(c_void_p))(self._visible),
            self._method(c_long, c_void_p, POINTER(c_void_p))(self._from_child),
            self._method(c_long, UiaPoint, POINTER(c_void_p))(self._from_point),
            self._method(c_long, POINTER(c_void_p))(self._document),
            self._method(c_long, POINTER(c_int))(self._supported),
        ]
        self._make("simple", methods, IID_TEXT)

    def _query(self, this, riid, result):
        target = str(GUID.from_address(riid)) if False else None
        try:
            value = ctypes.cast(riid, POINTER(GUID)).contents
            target = str(uuid.UUID(bytes_le=value.Data1.to_bytes(4, "little") +
                                   value.Data2.to_bytes(2, "little") +
                                   value.Data3.to_bytes(2, "little") +
                                   bytes(value.Data4)))
        except Exception:
            target = ""
        if target == str(IID_TEXT):
            self.refs += 1
            result[0] = self.simple
            return 0
        return -2147467262

    def _addref(self, this):
        self.refs += 1
        return self.refs

    def _release(self, this):
        self.refs -= 1
        return self.refs

    def _new_range(self, start, end):
        value = TextRange(self, start, end)
        self.provider.ranges.append(value)
        return value.simple

    def _text(self):
        text = getattr(self.widget, "text", "")
        return text() if callable(text) else str(text)

    def _selection(self, this, result):
        start, end = 0, 0
        widget = self.widget
        if hasattr(widget, "selection_range"):
            start, end = widget.selection_range()
        if start == end:
            result[0] = _array([])
        else:
            result[0] = _array([self._new_range(start, end)])
        return 0

    def _visible(self, this, result):
        text = self._text()
        result[0] = _array([self._new_range(0, len(text))])
        return 0

    def _from_child(self, this, child, result):
        text = self._text()
        result[0] = self._new_range(0, len(text))
        return 0

    def _from_point(self, this, point, result):
        widget = self.widget
        if hasattr(widget, "_index_from_point"):
            index = widget._index_from_point(point.x, point.y)
        else:
            index = 0
        result[0] = self._new_range(index, index)
        return 0

    def _document(self, this, result):
        text = self._text()
        result[0] = self._new_range(0, len(text))
        return 0

    def _supported(self, this, result):
        result[0] = SupportedTextSelection_Single
        return 0


class TextRange(_TextBase):
    def __init__(self, provider, start=0, end=0):
        self.provider = provider
        self.widget = provider.widget
        self.window = provider.window
        self.start = max(0, int(start))
        self.end = max(self.start, int(end))
        self.refs = 1
        import threading
        self._lock = threading.RLock()
        self._callbacks = []
        self._vtables = []
        self._cells = {}
        qi = self._method(c_long, POINTER(GUID), POINTER(c_void_p))(self._query)
        add = self._method(ctypes.c_ulong)(self._addref)
        release = self._method(ctypes.c_ulong)(self._release)
        methods = [
            qi, add, release,
            self._method(c_long, POINTER(c_void_p))(self._clone),
            self._method(c_long, c_void_p, POINTER(c_int))(self._compare),
            self._method(c_long, c_int, c_void_p, c_int,
                         POINTER(c_int))(self._compare_endpoints),
            self._method(c_long, c_int)(self._expand),
            self._method(c_long, c_int, VARIANT, wintypes.BOOL,
                         POINTER(c_void_p))(self._find_attribute),
            self._method(c_long, ctypes.c_wchar_p, wintypes.BOOL,
                         wintypes.BOOL, POINTER(c_void_p))(self._find_text),
            self._method(c_long, c_int, POINTER(VARIANT))(self._attribute),
            self._method(c_long, POINTER(c_void_p))(self._rectangles),
            self._method(c_long, POINTER(c_void_p))(self._enclosing),
            self._method(c_long, c_int, POINTER(c_void_p))(self._get_text),
            self._method(c_long, c_int, c_int, POINTER(c_int))(self._move),
            self._method(c_long, c_int, c_void_p, c_int)(self._move_endpoint_range),
            self._method(c_long, c_int, c_int, c_int,
                         POINTER(c_int))(self._move_endpoint_unit),
            self._method(c_long)(self._select),
            self._method(c_long)(self._add_selection),
            self._method(c_long)(self._remove_selection),
            self._method(c_long, wintypes.BOOL)(self._scroll),
            self._method(c_long, POINTER(c_void_p))(self._children),
        ]
        self._make("simple", methods, IID_RANGE)
        self._text_provider = provider
        self._text_provider._callbacks.extend(self._callbacks)

    def _query(self, this, riid, result):
        try:
            value = ctypes.cast(riid, POINTER(GUID)).contents
            target = str(uuid.UUID(bytes_le=value.Data1.to_bytes(4, "little") +
                                   value.Data2.to_bytes(2, "little") +
                                   value.Data3.to_bytes(2, "little") +
                                   bytes(value.Data4)))
        except Exception:
            target = ""
        if target == str(IID_RANGE):
            self.refs += 1
            result[0] = self.simple
            return 0
        return -2147467262

    def _addref(self, this):
        self.refs += 1
        return self.refs

    def _release(self, this):
        self.refs -= 1
        return self.refs

    def _text(self):
        text = self.widget.text
        return text() if callable(text) else str(text)

    def _clone(self, this, result):
        result[0] = TextRange(self.provider, self.start, self.end).simple
        return 0

    def _compare(self, this, other, result):
        if not other:
            result[0] = 1
        else:
            value = ctypes.cast(other, POINTER(c_void_p))
            result[0] = 0
        return 0

    def _compare_endpoints(self, this, endpoint, other, target, result):
        result[0] = 0
        return 0

    def _expand(self, this, unit):
        return 0

    def _find_attribute(self, this, attribute, value, backward, result):
        result[0] = None
        return 0

    def _find_text(self, this, text, backward, ignore_case, result):
        source = self._text()
        needle = text or ""
        haystack = source.lower() if ignore_case else source
        target = needle.lower() if ignore_case else needle
        if backward:
            index = haystack.rfind(target, 0, self.end)
        else:
            index = haystack.find(target, self.start)
        if index < 0 or not needle:
            result[0] = None
        else:
            value = TextRange(self.provider, index, index + len(needle))
            self.provider.provider.ranges.append(value)
            result[0] = value.simple
        return 0

    def _attribute(self, this, attribute, result):
        result[0] = VARIANT()
        return 0

    def _rectangles(self, this, result):
        text = self._text()[self.start:self.end]
        widget = self.widget
        rect = getattr(widget, "rect", None)
        if rect is None or not text:
            result[0] = _double_array([])
            return 0
        from .uia_provider import user32
        point = wintypes.POINT(0, 0)
        user32.ClientToScreen(ctypes.c_void_p(self.provider.provider.window.hwnd),
                              byref(point))
        width = 0
        try:
            width = widget._measure_prefix(text)
        except Exception:
            width = len(text) * 8
        height = 18
        if getattr(widget, "layout", None) is not None:
            height = widget.layout.line_height
        result[0] = _double_array([point.x + rect.x + 6,
                                   point.y + rect.y + 6, width, height])
        return 0

    def _enclosing(self, this, result):
        result[0] = self.provider.provider.simple
        self.provider.provider.refs += 1
        return 0

    def _get_text(self, this, max_length, result):
        text = self._text()[self.start:self.end]
        if max_length > 0:
            text = text[:max_length]
        bstr = oleaut32.SysAllocString(text)
        result[0] = ctypes.cast(bstr, c_void_p)
        return 0

    def _move(self, this, unit, count, moved):
        text = self._text()
        old = self.start
        if unit == 0:  # Character
            self.start = max(0, min(len(text), self.start + count))
        elif unit == 2:  # Word
            if count < 0:
                self.start = text.rfind(" ", 0, self.start) + 1
            else:
                end = text.find(" ", self.start)
                self.start = len(text) if end < 0 else end + 1
        elif unit == 3:  # Line
            if count < 0:
                self.start = text.rfind("\n", 0, self.start) + 1
            else:
                end = text.find("\n", self.start)
                self.start = len(text) if end < 0 else end + 1
        elif unit in (4, 5):  # Paragraph/Page
            self.start = 0 if count < 0 else len(text)
        elif unit == 6:  # Document
            self.start = 0 if count < 0 else len(text)
        self.end = self.start
        if moved:
            moved[0] = 1 if self.start != old else 0
        return 0

    def _move_endpoint_range(self, this, endpoint, other, target):
        return 0

    def _move_endpoint_unit(self, this, endpoint, unit, count, moved):
        text = self._text()
        if endpoint == 0:
            self.start = max(0, min(self.end, self.start + count))
        else:
            self.end = max(self.start, min(len(text), self.end + count))
        if moved:
            moved[0] = count
        return 0

    def _select(self, this):
        widget = self.widget
        if hasattr(widget, "anchor"):
            widget.anchor = self.start
            widget.cursor = self.end
            widget.update()
        return 0

    def _add_selection(self, this):
        return self._select(this)

    def _remove_selection(self, this):
        return 0

    def _scroll(self, this, align):
        return 0

    def _children(self, this, result):
        result[0] = _array([])
        return 0


oleaut32.SafeArrayCreateVector.argtypes = [ctypes.c_ushort, c_long,
                                           ctypes.c_ulong]
oleaut32.SafeArrayCreateVector.restype = c_void_p
oleaut32.SafeArrayPutElement.argtypes = [c_void_p, POINTER(c_long), c_void_p]
oleaut32.SafeArrayPutElement.restype = c_long
