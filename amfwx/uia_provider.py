"""Optional UIA COM provider for AMFWX (ctypes, opt-in).

Implements a minimal IRawElementProviderSimple/Fragment/FragmentRoot/Invoke
tree. It is intentionally opt-in because UIA calls come from COM threads.
"""

from __future__ import annotations

import ctypes
from ctypes import POINTER, byref, c_double, c_int, c_long, c_uint, c_void_p
from ctypes import wintypes

user32 = ctypes.WinDLL("user32")
oleaut32 = ctypes.WinDLL("oleaut32")
uia = ctypes.WinDLL("uiautomationcore")

UIA_ROOT_OBJECT_ID = -25
user32.ClientToScreen.argtypes = [c_void_p, POINTER(wintypes.POINT)]
user32.ClientToScreen.restype = wintypes.BOOL
uia.UiaHostProviderFromHwnd.argtypes = [c_void_p, POINTER(c_void_p)]
uia.UiaHostProviderFromHwnd.restype = c_long
oleaut32.SysAllocString.argtypes = [ctypes.c_wchar_p]
oleaut32.SysAllocString.restype = c_void_p
uia.UiaClientsAreListening.restype = wintypes.BOOL
uia.UiaRaiseAutomationEvent.argtypes = [c_void_p, c_int]
uia.UiaRaiseAutomationEvent.restype = c_long
uia.UiaRaiseStructureChangedEvent.argtypes = [c_void_p, c_int, c_void_p]
uia.UiaRaiseStructureChangedEvent.restype = c_long
WM_GETOBJECT = 0x003D
VT_I4 = 3
VT_BSTR = 8
VT_EMPTY = 0
ProviderOptions_ServerSideProvider = 1
ProviderOptions_UseComThreading = 0x20
UIA_NamePropertyId = 30005
UIA_ControlTypePropertyId = 30003
UIA_IsEnabledPropertyId = 30010
UIA_IsOffscreenPropertyId = 30022
UIA_InvokePatternId = 10000
ControlType_Window = 50032
ControlType_Button = 50000
ControlType_Edit = 50004
ControlType_CheckBox = 50002
ControlType_Text = 50020
ControlType_Pane = 50033
ControlType_DataGrid = 50028
ControlType_Tree = 50023
ControlType_DataItem = 50029
ControlType_TreeItem = 50024


class GUID(ctypes.Structure):
    _fields_ = [("Data1", c_uint), ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort),
                ("Data4", ctypes.c_ubyte * 8)]

    def __str__(self):
        import uuid
        raw = (self.Data1.to_bytes(4, "little") +
               self.Data2.to_bytes(2, "little") +
               self.Data3.to_bytes(2, "little") +
               bytes(self.Data4))
        return str(uuid.UUID(bytes_le=raw))

    @classmethod
    def parse(cls, text):
        import uuid
        value = uuid.UUID(text)
        return cls(value.time_low, value.time_mid, value.time_hi_version,
                   (ctypes.c_ubyte * 8)(*value.bytes[8:]))


IID_SIMPLE = GUID.parse("d6dd68d1-86fd-4332-8666-9abedea2d24c")
IID_FRAGMENT = GUID.parse("f7063da8-8359-439c-9297-bbc5299a7d87")
IID_ROOT = GUID.parse("620ce2a5-ab8f-40a9-86cb-de3c75599b58")
IID_INVOKE = GUID.parse("54fcb24b-e18e-47a2-b4d3-eccbe77599a2")
IID_VALUE = GUID.parse("c7935180-6fb3-4201-b174-7df73adbf64a")
IID_SELECTION = GUID.parse("fb8b03af-3bdf-48d4-bd36-1a65793be168")
IID_EXPAND = GUID.parse("d847d3a5-cab0-4a98-8c32-ecb45c59ad24")
IID_RANGE = GUID.parse("36dc7aef-33e6-4691-afe1-2be7274b3d33")
IID_TOGGLE = GUID.parse("56d00bd0-c4f4-433c-a836-1a52a57e0892")
IID_GRID = GUID.parse("b17d6187-0907-464b-a168-0ef17a1572b1")
IID_TABLE = GUID.parse("9c860395-97b3-490a-b52a-858cc22af166")
IID_TRANSFORM = GUID.parse("6829ddc4-4f91-4ffa-b86f-bd3e2987cb4c")
UIA_ValuePatternId = 10002
UIA_TextPatternId = 10014
UIA_SelectionPatternId = 10001
UIA_ExpandCollapsePatternId = 10005
UIA_RangeValuePatternId = 10003
UIA_TogglePatternId = 10015
UIA_GridPatternId = 10006
UIA_TablePatternId = 10009
UIA_TransformPatternId = 10016
UIA_ValueValuePropertyId = 30045
UIA_FocusChangedEventId = 20005
UIA_InvokeInvokedEventId = 20009
UIA_ValueValuePropertyChangedEventId = 20012
UIA_StructureChangedEventId = 20002


class VARIANT(ctypes.Structure):
    _fields_ = [("vt", ctypes.c_ushort), ("r1", ctypes.c_ushort),
                ("r2", ctypes.c_ushort), ("r3", ctypes.c_ushort),
                ("value", ctypes.c_longlong), ("value2", ctypes.c_longlong)]


class UiaRect(ctypes.Structure):
    _fields_ = [("left", c_double), ("top", c_double),
                ("width", c_double), ("height", c_double)]


_objects = {}


def _guid(pointer):
    value = ctypes.cast(pointer, POINTER(GUID)).contents
    import uuid
    raw = value.Data1.to_bytes(4, "little") + \
        value.Data2.to_bytes(2, "little") + \
        value.Data3.to_bytes(2, "little") + bytes(value.Data4)
    return str(uuid.UUID(bytes_le=raw))


def _variant_int(value):
    variant = VARIANT()
    variant.vt = VT_I4
    variant.value = int(value)
    return variant


def _variant_bool(value):
    variant = VARIANT()
    variant.vt = 11
    variant.value = -1 if value else 0
    return variant


def _variant_string(text):
    variant = VARIANT()
    variant.vt = VT_BSTR
    bstr = oleaut32.SysAllocString(str(text))
    variant.value = ctypes.cast(bstr, c_void_p).value or 0
    return variant


class _VirtualCell:
    def __init__(self, text, rect, row, column):
        self.text = text
        self.rect = rect
        self.row = row
        self.column = column
        self.children = []
        self.enabled = True
        self.focusable = False


class _VirtualRow:
    def __init__(self, text, rect, item=None):
        self.text = text
        self.rect = rect
        self.item = item
        self.children = []
        self.enabled = True
        self.focusable = False


class Provider:
    def __init__(self, window, widget, parent=None, root=False):
        self.window = window
        self.widget = widget
        self.parent = parent
        self.root = root
        self.refs = 1
        self.children = []
        self.ranges = []
        self._callbacks = []
        self._vtables = []
        self._cells = {}
        import threading
        self._lock = threading.RLock()
        self._build()

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

    def _build(self):
        qi = self._method(c_long, POINTER(GUID), POINTER(c_void_p))(self._query)
        add = self._method(ctypes.c_ulong)(self._addref)
        release = self._method(ctypes.c_ulong)(self._release)
        simple = [qi, add, release,
                  self._method(c_long, POINTER(c_int))(self._options),
                  self._method(c_long, POINTER(c_void_p))(self._host),
                  self._method(c_long, c_int, POINTER(c_void_p))(self._pattern),
                  self._method(c_long, c_int, POINTER(VARIANT))(self._property)]
        self._make("simple", simple, IID_SIMPLE)
        fragment = [qi, add, release,
                    self._method(c_long, c_int, POINTER(c_void_p))(self._navigate),
                    self._method(c_long, POINTER(c_void_p))(self._runtime),
                    self._method(c_long, POINTER(UiaRect))(self._bounds),
                    self._method(c_long, POINTER(c_void_p))(self._embedded),
                    self._method(c_long)(self._focus),
                    self._method(c_long, POINTER(c_void_p))(self._fragment_root)]
        self._make("fragment", fragment, IID_FRAGMENT)
        if self.root:
            transform = [qi, add, release,
                         self._method(c_long, ctypes.c_double, ctypes.c_double)(self._transform_move),
                         self._method(c_long, ctypes.c_double, ctypes.c_double)(self._transform_resize),
                         self._method(c_long, ctypes.c_double)(self._transform_rotate),
                         self._method(c_long, POINTER(wintypes.BOOL))(self._can_move),
                         self._method(c_long, POINTER(wintypes.BOOL))(self._can_resize),
                         self._method(c_long, POINTER(wintypes.BOOL))(self._can_rotate)]
            self._make("transform", transform, IID_TRANSFORM)
            root = [qi, add, release,
                    self._method(c_long, c_double, c_double,
                                 POINTER(c_void_p))(self._from_point),
                    self._method(c_long, POINTER(c_void_p))(self._get_focus)]
            self._make("root", root, IID_ROOT)
        if type(self.widget).__name__ == "Button":
            invoke = [qi, add, release,
                      self._method(c_long)(self._invoke)]
            self._make("invoke", invoke, IID_INVOKE)
        if type(self.widget).__name__ in ("LineEdit", "TextEdit"):
            value = [qi, add, release,
                     self._method(c_long, ctypes.c_wchar_p)(self._set_value),
                     self._method(c_long, POINTER(c_void_p))(self._get_value),
                     self._method(c_long, POINTER(wintypes.BOOL))(self._get_readonly)]
            self._make("value", value, IID_VALUE)
        if type(self.widget).__name__ in ("LineEdit", "TextEdit"):
            from .uia_text import TextProvider
            self.text_provider = TextProvider(self)
            self.text_iface = self.text_provider.simple
        if type(self.widget).__name__ in ("TableView", "TreeView"):
            selection = [qi, add, release,
                         self._method(c_long, POINTER(c_void_p))(self._get_selection),
                         self._method(c_long, POINTER(wintypes.BOOL))(self._selection_multi),
                         self._method(c_long, POINTER(wintypes.BOOL))(self._selection_required)]
            self._make("selection", selection, IID_SELECTION)
        if type(self.widget).__name__ == "TableView":
            grid = [qi, add, release,
                    self._method(c_long, c_int, c_int,
                                 POINTER(c_void_p))(self._grid_item),
                    self._method(c_long, POINTER(c_int))(self._grid_rows),
                    self._method(c_long, POINTER(c_int))(self._grid_columns)]
            self._make("grid", grid, IID_GRID)
            table = [qi, add, release,
                     self._method(c_long, POINTER(c_void_p))(self._table_rows),
                     self._method(c_long, POINTER(c_void_p))(self._table_columns),
                     self._method(c_long, POINTER(c_int))(self._table_major)]
            self._make("table", table, IID_TABLE)
        if type(self.widget).__name__ == "CheckBox":
            toggle = [qi, add, release,
                      self._method(c_long)(self._toggle),
                      self._method(c_long, POINTER(c_int))(self._toggle_state)]
            self._make("toggle", toggle, IID_TOGGLE)
        if type(self.widget).__name__ in ("Slider", "ScrollBar"):
            range_value = [qi, add, release,
                           self._method(c_long, ctypes.c_double)(self._range_set),
                           self._method(c_long, POINTER(ctypes.c_double))(self._range_value),
                           self._method(c_long, POINTER(ctypes.c_double))(self._range_max),
                           self._method(c_long, POINTER(ctypes.c_double))(self._range_min),
                           self._method(c_long, POINTER(ctypes.c_double))(self._range_large),
                           self._method(c_long, POINTER(ctypes.c_double))(self._range_small),
                           self._method(c_long, POINTER(wintypes.BOOL))(self._range_readonly)]
            self._make("range", range_value, IID_RANGE)
        if type(self.widget).__name__ == "_VirtualRow" and getattr(self.widget, "item", None) is not None:
            expand = [qi, add, release,
                      self._method(c_long)(self._expand),
                      self._method(c_long)(self._collapse),
                      self._method(c_long, POINTER(c_int))(self._expand_state)]
            self._make("expand", expand, IID_EXPAND)
        for child in getattr(self.widget, "children", []):
            self.children.append(Provider(self.window, child, self))
        if type(self.widget).__name__ == "TableView":
            from .canvas import Rect
            table = self.widget
            width = table.rect.w if table.rect else 0
            for index, row in enumerate(table.rows):
                rect = Rect(table.rect.x if table.rect else 0,
                            (table.rect.y if table.rect else 0) +
                            table.header_height + index * table.row_height,
                            width, table.row_height)
                virtual = _VirtualRow(" ".join(str(value) for value in row),
                                      rect)
                cell_width = width / max(1, len(row)) if width else 0
                virtual.children = [
                    _VirtualCell(str(value),
                                 Rect(rect.x + column * cell_width, rect.y,
                                      cell_width, rect.h), index, column)
                    for column, value in enumerate(row)]
                child = Provider(self.window, virtual, self)
                self.children.append(child)
        if type(self.widget).__name__ == "TreeView":
            from .canvas import Rect
            tree = self.widget
            for index, (item, depth) in enumerate(tree._flatten(tree.items)):
                rect = Rect(tree.rect.x if tree.rect else 0,
                            (tree.rect.y if tree.rect else 0) + 4 +
                            index * 24, tree.rect.w if tree.rect else 0, 24)
                virtual = _VirtualRow(item.label, rect, item)
                child = Provider(self.window, virtual, self)
                self.children.append(child)

    def _make(self, name, functions, iid):
        array = (c_void_p * len(functions))(*functions)
        self._vtables.append(array)
        holder = ctypes.c_void_p(ctypes.addressof(array))
        self._vtables.append(holder)
        interface = ctypes.c_void_p(ctypes.addressof(holder))
        self._cells[name] = interface
        setattr(self, name, interface)
        _objects[interface.value] = self
        if name == "simple":
            self.simple = interface
        if name == "fragment":
            self.fragment = interface
        if name == "root":
            self.root_iface = interface
        if name == "invoke":
            self.invoke = interface
        if name == "value":
            self.value_iface = interface
        if name == "selection":
            self.selection_iface = interface

    def _query(self, this, riid, result):
        target = _guid(riid)
        table = {str(IID_SIMPLE): "simple", str(IID_FRAGMENT): "fragment",
                 str(IID_ROOT): "root", str(IID_INVOKE): "invoke",
                 str(IID_VALUE): "value",
                 str(IID_SELECTION): "selection",
                 str(IID_EXPAND): "expand",
                 str(IID_RANGE): "range",
                 str(IID_TOGGLE): "toggle",
                 str(IID_GRID): "grid", str(IID_TABLE): "table",
                 str(IID_TRANSFORM): "transform"}
        name = table.get(target)
        if name is None or name not in self._cells:
            return -2147467262  # E_NOINTERFACE
        self.refs += 1
        result[0] = self._cells[name]
        return 0

    def _addref(self, this):
        self.refs += 1
        return self.refs

    def _release(self, this):
        self.refs -= 1
        if self.refs <= 0:
            for key, value in list(_objects.items()):
                if value is self:
                    _objects.pop(key, None)
        return self.refs

    def _options(self, this, options):
        options[0] = ProviderOptions_ServerSideProvider
        return 0

    def _pattern(self, this, pattern, result):
        if pattern == UIA_InvokePatternId and hasattr(self, "invoke"):
            self.refs += 1
            result[0] = self.invoke
        elif pattern == UIA_ValuePatternId and hasattr(self, "value_iface"):
            self.refs += 1
            result[0] = self.value_iface
        elif pattern == UIA_TextPatternId and hasattr(self, "text_iface"):
            self.refs += 1
            result[0] = self.text_iface
        elif pattern == UIA_SelectionPatternId and hasattr(self, "selection"):
            self.refs += 1
            result[0] = self.selection
        elif pattern == UIA_ExpandCollapsePatternId and hasattr(self, "expand"):
            self.refs += 1
            result[0] = self.expand
        elif pattern == UIA_RangeValuePatternId and hasattr(self, "range"):
            self.refs += 1
            result[0] = self.range
        elif pattern == UIA_TogglePatternId and hasattr(self, "toggle"):
            self.refs += 1
            result[0] = self.toggle
        elif pattern == UIA_GridPatternId and hasattr(self, "grid"):
            self.refs += 1
            result[0] = self.grid
        elif pattern == UIA_TablePatternId and hasattr(self, "table"):
            self.refs += 1
            result[0] = self.table
        elif pattern == UIA_TransformPatternId and hasattr(self, "transform"):
            self.refs += 1
            result[0] = self.transform
        else:
            result[0] = None
        return 0

    def _property(self, this, property_id, result):
        widget = self.widget
        if property_id in (10016, 10017):
            result[0] = _variant_bool(True)
            return 0
        if property_id == UIA_NamePropertyId:
            name = (self.window.title if self.root else
                    getattr(widget, "text", "") or getattr(widget, "title", ""))
            result[0] = _variant_string(name)
        elif property_id == UIA_ControlTypePropertyId:
            result[0] = _variant_int(self._control_type())
        elif property_id == UIA_IsEnabledPropertyId:
            result[0] = _variant_bool(getattr(widget, "enabled", True))
        elif property_id == UIA_IsOffscreenPropertyId:
            result[0] = _variant_bool(False)
        else:
            result[0] = VARIANT()
        return 0

    def _control_type(self):
        if self.root:
            return ControlType_Window
        if type(self.widget).__name__ == "_VirtualCell":
            return ControlType_DataItem
        if type(self.widget).__name__ == "_VirtualRow":
            return ControlType_TreeItem if getattr(self.widget, "item", None) is not None else ControlType_DataItem
        name = type(self.widget).__name__
        return {"Window": ControlType_Window, "Button": ControlType_Button,
                "LineEdit": ControlType_Edit, "TextEdit": ControlType_Edit,
                "CheckBox": ControlType_CheckBox, "Label": ControlType_Text,
                "TableView": ControlType_DataGrid,
                "TreeView": ControlType_Tree}.get(name, ControlType_Pane)

    def _host(self, this, result):
        result[0] = None
        if self.root:
            host = c_void_p()
            try:
                uia.UiaHostProviderFromHwnd(ctypes.c_void_p(self.window.hwnd),
                                            byref(host))
                result[0] = host
            except Exception:
                pass
        return 0

    def _navigate(self, this, direction, result):
        result[0] = None
        if direction == 0 and self.parent is not None:  # Parent
            result[0] = self.parent.fragment
        elif direction == 1 and self.children:  # FirstChild
            result[0] = self.children[0].fragment
        elif direction == 2 and self.children:  # LastChild
            result[0] = self.children[-1].fragment
        elif direction == 3 and self.parent is not None:  # NextSibling
            siblings = self.parent.children
            index = siblings.index(self)
            if index + 1 < len(siblings):
                result[0] = siblings[index + 1].fragment
        elif direction == 4 and self.parent is not None:  # PreviousSibling
            siblings = self.parent.children
            index = siblings.index(self)
            if index > 0:
                result[0] = siblings[index - 1].fragment
        if result[0] is not None:
            self.refs += 1
        return 0

    def _runtime(self, this, result):
        result[0] = None
        return 0

    def _bounds(self, this, result):
        rect = getattr(self.widget, "rect", None)
        point = wintypes.POINT(0, 0)
        user32.ClientToScreen(ctypes.c_void_p(self.window.hwnd), byref(point))
        left = point.x + (rect.x if rect else 0)
        top = point.y + (rect.y if rect else 0)
        result[0] = UiaRect(left, top, rect.w if rect else 0,
                            rect.h if rect else 0)
        return 0

    def _embedded(self, this, result):
        result[0] = None
        return 0

    def _focus(self, this):
        if hasattr(self.window, "set_focus") and getattr(self.widget, "focusable", False):
            self.window.set_focus(self.widget)
        return 0

    def _fragment_root(self, this, result):
        root = self
        while root.parent is not None:
            root = root.parent
        result[0] = getattr(root, "root_iface", None)
        if result[0] is not None:
            self.refs += 1
        return 0

    def _from_point(self, this, x, y, result):
        target = self._find(x, y)
        result[0] = target.fragment if target else None
        if result[0] is not None:
            self.refs += 1
        return 0

    def _find(self, screen_x, screen_y):
        for provider in self.children:
            found = provider._find(screen_x, screen_y)
            if found:
                return found
        rect = getattr(self.widget, "rect", None)
        point = wintypes.POINT(0, 0)
        user32.ClientToScreen(ctypes.c_void_p(self.window.hwnd), byref(point))
        if rect and point.x + rect.x <= screen_x <= point.x + rect.right and \
                point.y + rect.y <= screen_y <= point.y + rect.bottom:
            return self
        return None

    def _get_focus(self, this, result):
        result[0] = None
        focus = getattr(self.window, "focus_widget", None)
        if focus is not None:
            found = self._find_widget(focus)
            if found:
                result[0] = found.fragment
                self.refs += 1
        return 0

    def _find_widget(self, widget):
        if self.widget is widget:
            return self
        for child in self.children:
            found = child._find_widget(widget)
            if found:
                return found
        return None

    def _transform_move(self, this, x, y):
        user32.SetWindowPos(ctypes.c_void_p(self.window.hwnd), None,
                            int(x), int(y), 0, 0, 0x0001 | 0x0004)
        return 0

    def _transform_resize(self, this, width, height):
        user32.SetWindowPos(ctypes.c_void_p(self.window.hwnd), None, 0, 0,
                            int(width), int(height), 0x0002 | 0x0004)
        return 0

    def _transform_rotate(self, this, degrees):
        return 0

    def _can_move(self, this, result):
        result[0] = 1
        return 0

    def _can_resize(self, this, result):
        result[0] = 1
        return 0

    def _can_rotate(self, this, result):
        result[0] = 0
        return 0

    def _grid_item(self, this, row, column, result):
        if 0 <= row < len(self.children):
            cells = self.children[row].children
            if 0 <= column < len(cells):
                cells[column].refs += 1
                result[0] = cells[column].simple
                return 0
        result[0] = None
        return -2147024809  # E_INVALIDARG

    def _grid_rows(self, this, result):
        result[0] = len(self.children)
        return 0

    def _grid_columns(self, this, result):
        result[0] = len(self.children[0].children) if self.children else 0
        return 0

    def _table_rows(self, this, result):
        result[0] = None
        return 0

    def _table_columns(self, this, result):
        result[0] = None
        return 0

    def _table_major(self, this, result):
        result[0] = 0
        return 0

    def _toggle(self, this):
        action = getattr(self.widget, "toggle", None)
        if action is not None:
            action()
            self._refresh()
        return 0

    def _toggle_state(self, this, result):
        result[0] = 1 if getattr(self.widget, "checked", False) else 0
        return 0

    def _range_set(self, this, value):
        setter = getattr(self.widget, "set_value", None)
        if setter is not None:
            setter(value)
        elif hasattr(self.widget, "value"):
            self.widget.value = int(value)
        self._refresh()
        return 0

    def _range_value(self, this, result):
        value = getattr(self.widget, "value", 0)
        result[0] = float(value() if callable(value) else value)
        return 0

    def _range_max(self, this, result):
        result[0] = float(getattr(self.widget, "maximum", 100))
        return 0

    def _range_min(self, this, result):
        result[0] = float(getattr(self.widget, "minimum", 0))
        return 0

    def _range_large(self, this, result):
        result[0] = 10.0
        return 0

    def _range_small(self, this, result):
        result[0] = 1.0
        return 0

    def _range_readonly(self, this, result):
        result[0] = 0
        return 0

    def _expand(self, this):
        item = getattr(self.widget, "item", None)
        if item is not None and item.children:
            item.expanded = True
            self._refresh()
            provider = getattr(self.window, "uia_provider", None)
            if provider is not None:
                provider.structure_changed(self)
        return 0

    def _collapse(self, this):
        item = getattr(self.widget, "item", None)
        if item is not None and item.children:
            item.expanded = False
            self._refresh()
            provider = getattr(self.window, "uia_provider", None)
            if provider is not None:
                provider.structure_changed(self)
        return 0

    def _expand_state(self, this, result):
        item = getattr(self.widget, "item", None)
        if item is None or not item.children:
            result[0] = 3  # LeafNode
        else:
            result[0] = 1 if item.expanded else 0
        return 0

    def _refresh(self):
        window = self.window
        if window is not None:
            window.invalidate()

    def _get_selection(self, this, result):
        from .uia_text import _array
        selected = getattr(self.widget, "selected", None)
        if type(self.widget).__name__ == "TableView" and selected not in (None, -1):
            if 0 <= selected < len(self.children):
                result[0] = _array([self.children[selected].simple])
                return 0
        if type(self.widget).__name__ == "TreeView":
            target = getattr(self.widget, "selected", None)
            for child in self.children:
                if getattr(child.widget, "item", None) is target:
                    result[0] = _array([child.simple])
                    return 0
        result[0] = _array([])
        return 0

    def _selection_multi(self, this, result):
        result[0] = 0
        return 0

    def _selection_required(self, this, result):
        result[0] = 0
        return 0

    def _set_value(self, this, text):
        setter = getattr(self.widget, "set_text", None)
        if setter:
            setter(text or "")
        provider = getattr(self.window, "uia_provider", None)
        if provider is not None:
            provider.raise_event(UIA_ValueValuePropertyChangedEventId, self)
        return 0

    def _get_value(self, this, result):
        text = getattr(self.widget, "text", "")
        bstr = oleaut32.SysAllocString(str(text() if callable(text) else text))
        result[0] = ctypes.cast(bstr, c_void_p)
        return 0

    def _get_readonly(self, this, result):
        result[0] = 0
        return 0

    def _invoke(self, this):
        activate = getattr(self.widget, "activate", None)
        if activate:
            activate()
        provider = getattr(self.window, "uia_provider", None)
        if provider is not None:
            provider.raise_event(UIA_InvokeInvokedEventId, self)
        return 0


class UiaProvider:
    def raise_event(self, event_id, provider):
        try:
            if uia.UiaClientsAreListening():
                uia.UiaRaiseAutomationEvent(provider.simple, event_id)
        except Exception:
            pass

    def structure_changed(self, provider):
        try:
            if uia.UiaClientsAreListening():
                uia.UiaRaiseStructureChangedEvent(provider.simple, 2, None)
        except Exception:
            pass

    def focus_event(self, widget):
        found = self.root._find_widget(widget)
        if found is not None:
            self.raise_event(UIA_FocusChangedEventId, found)

    def __init__(self, window):
        self.window = window
        self.root = Provider(window, window.root, root=True)
        _objects[self.root.simple.value] = self.root

    def handle_getobject(self, hwnd=None):
        try:
            uia.UiaReturnRawElementProvider.argtypes = [
                c_void_p, ctypes.c_size_t, ctypes.c_ssize_t, c_void_p]
            uia.UiaReturnRawElementProvider.restype = ctypes.c_ssize_t
            return uia.UiaReturnRawElementProvider(
                ctypes.c_void_p(hwnd or self.window.hwnd), UIA_ROOT_OBJECT_ID, 0,
                self.root.simple)
        except Exception:
            return 0
