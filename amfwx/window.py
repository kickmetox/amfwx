"""AMFWX Win32 window + event loop + DIB presentation."""

from __future__ import annotations

import ctypes
from ctypes import POINTER, byref, c_int, c_void_p, c_wchar_p, wintypes

from .canvas import Canvas, Color, Rect
from .theme import DARK, Theme, get_theme
from .widgets import BoxLayout, Widget

user32 = ctypes.WinDLL("user32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32")
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
try:
    user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
    user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    pass

class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", ctypes.c_uint), ("lpfnWndProc", c_void_p),
        ("cbClsExtra", c_int), ("cbWndExtra", c_int),
        ("hInstance", c_void_p), ("hIcon", c_void_p),
        ("hCursor", c_void_p), ("hbrBackground", c_void_p),
        ("lpszMenuName", c_wchar_p), ("lpszClassName", c_wchar_p),
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint), ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long), ("biPlanes", ctypes.c_ushort),
        ("biBitCount", ctypes.c_ushort), ("biCompression", ctypes.c_uint),
        ("biSizeImage", ctypes.c_uint), ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", ctypes.c_uint),
        ("biClrImportant", ctypes.c_uint),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER),
                ("bmiColors", ctypes.c_uint * 3)]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", c_void_p), ("fErase", c_int), ("rcPaint", wintypes.RECT),
        ("fRestore", c_int), ("fIncUpdate", c_int),
        ("rgbReserved", ctypes.c_byte * 32),
    ]


class POINTER_INFO(ctypes.Structure):
    _fields_ = [
        ("pointerType", ctypes.c_uint), ("pointerId", ctypes.c_uint),
        ("frameId", ctypes.c_uint), ("pointerFlags", ctypes.c_uint),
        ("sourceDevice", c_void_p), ("hwndTarget", c_void_p),
        ("ptPixelLocation", wintypes.POINT),
        ("ptHimetricLocation", wintypes.POINT),
        ("ptPixelLocationRaw", wintypes.POINT),
        ("ptHimetricLocationRaw", wintypes.POINT),
        ("dwTime", ctypes.c_uint), ("historyCount", ctypes.c_uint),
        ("inputData", ctypes.c_int), ("dwKeyStates", ctypes.c_uint),
        ("performanceCount", ctypes.c_ulonglong),
        ("buttonChangeType", ctypes.c_int),
    ]


WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, c_void_p, ctypes.c_uint,
                             ctypes.c_ulonglong, ctypes.c_ulonglong)
kernel32.GetModuleHandleW.restype = c_void_p
kernel32.GetModuleHandleW.argtypes = [c_wchar_p]
user32.LoadCursorW.restype = c_void_p
user32.LoadCursorW.argtypes = [c_void_p, c_void_p]
user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
user32.RegisterClassW.restype = ctypes.c_ushort
user32.DefWindowProcW.restype = ctypes.c_longlong
user32.DefWindowProcW.argtypes = [c_void_p, ctypes.c_uint,
                                  ctypes.c_ulonglong, ctypes.c_ulonglong]
user32.CallWindowProcW.argtypes = [c_void_p, c_void_p, ctypes.c_uint,
                                   ctypes.c_size_t, ctypes.c_ssize_t]
user32.CallWindowProcW.restype = ctypes.c_ssize_t
user32.BeginPaint.restype = c_void_p
user32.BeginPaint.argtypes = [c_void_p, ctypes.POINTER(PAINTSTRUCT)]
user32.EndPaint.argtypes = [c_void_p, ctypes.POINTER(PAINTSTRUCT)]
user32.ShowWindow.argtypes = [c_void_p, c_int]
user32.UpdateWindow.argtypes = [c_void_p]
user32.InvalidateRect.argtypes = [c_void_p, c_void_p, ctypes.c_int]
user32.DestroyWindow.argtypes = [c_void_p]
user32.PostQuitMessage.argtypes = [c_int]
user32.PostMessageW.argtypes = [c_void_p, ctypes.c_uint,
                                ctypes.c_ulonglong, ctypes.c_ulonglong]
user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), c_void_p,
                                ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), c_void_p,
                               ctypes.c_uint, ctypes.c_uint]
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = ctypes.c_longlong
user32.ScreenToClient.argtypes = [c_void_p, ctypes.POINTER(wintypes.POINT)]
shell32.DragQueryFileW.argtypes = [c_void_p, ctypes.c_uint, c_wchar_p, ctypes.c_uint]
shell32.DragQueryFileW.restype = ctypes.c_uint
shell32.DragQueryPoint.argtypes = [c_void_p, ctypes.POINTER(wintypes.POINT)]
shell32.DragFinish.argtypes = [c_void_p]
user32.SetCapture.argtypes = [c_void_p]
user32.ReleaseCapture.argtypes = []
user32.GetPointerInfo.argtypes = [ctypes.c_uint,
                                  ctypes.POINTER(POINTER_INFO)]
user32.GetPointerInfo.restype = ctypes.c_int
gdi32.StretchDIBits.restype = c_int
gdi32.StretchDIBits.argtypes = [
    c_void_p, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int,
    c_void_p, c_void_p, ctypes.c_uint, ctypes.c_uint,
]

WM_PAINT = 0x000F
WM_SIZE = 0x0005
WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_QUIT = 0x0012
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_KEYDOWN = 0x0100
WM_CHAR = 0x0102
WM_MOUSEWHEEL = 0x020A
WM_POINTERUPDATE = 0x0245
WM_POINTERDOWN = 0x0246
WM_POINTERUP = 0x0247
WM_POINTERENTER = 0x0249
WM_POINTERLEAVE = 0x024A
WM_IME_STARTCOMPOSITION = 0x010D
WM_IME_ENDCOMPOSITION = 0x010E
WM_IME_COMPOSITION = 0x010F
WM_GETOBJECT = 0x003D
WM_DPICHANGED = 0x02E0
WM_DROPFILES = 0x0233
WM_RBUTTONUP = 0x0205
WM_APP_INVOKE = 0x8000 + 101
WM_COMMAND = 0x0111
UIA_ROOT_OBJECT_ID = -25
WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000
CW_USEDEFAULT = -2147483648
CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001
IDC_ARROW = 32512
COLOR_WINDOW = 5
SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0


_windows = {}
_window_proc = None
_class_name = "AMFWX.Window"
_class_registered = False
_a11y_class = "AMFWX.Proxy"
_a11y_registered = False
_proxy_objects = {}
_proxy_key_objects = {}
_proxy_wndproc = None
_proxy_key_wndproc = None


def _wndproc(hwnd, msg, wparam, lparam):
    window = _windows.get(int(hwnd))
    if window is None:
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
    if msg == WM_COMMAND:
        window._proxy_command(int(wparam), int(lparam))
        return 0
    if msg == WM_APP_INVOKE:
        window._handle_invoke(int(wparam))
        return 0
    if msg == WM_PAINT:
        if int(hwnd) != int(window.hwnd):
            return 0
        window._paint()
        return 0
    if msg == WM_SIZE:
        width = lparam & 0xFFFF
        height = (lparam >> 16) & 0xFFFF
        if width and height:
            window._resize(width, height)
        return 0
    if msg == WM_LBUTTONDOWN:
        x = ctypes.c_short(wparam & 0xFFFF).value
        y = ctypes.c_short((wparam >> 16) & 0xFFFF).value
        window._mouse_down(int(x / window.dpi_scale), int(y / window.dpi_scale))
        return 0
    if msg == WM_RBUTTONUP:
        x = ctypes.c_short(wparam & 0xFFFF).value
        y = ctypes.c_short((wparam >> 16) & 0xFFFF).value
        window._context_menu(int(x / window.dpi_scale),
                             int(y / window.dpi_scale))
        return 0
    if msg == WM_LBUTTONUP:
        x = ctypes.c_short(wparam & 0xFFFF).value
        y = ctypes.c_short((wparam >> 16) & 0xFFFF).value
        window._mouse_up(int(x / window.dpi_scale), int(y / window.dpi_scale))
        return 0
    if msg == WM_MOUSEMOVE:
        x = ctypes.c_short(wparam & 0xFFFF).value
        y = ctypes.c_short((wparam >> 16) & 0xFFFF).value
        window._mouse_move(int(x / window.dpi_scale), int(y / window.dpi_scale))
        return 0
    if msg == WM_KEYDOWN:
        window._key_down(int(wparam), window._modifiers())
        return 0
    if msg == WM_CHAR:
        window._char_input(chr(wparam & 0xFFFF))
        return 0
    if msg == WM_MOUSEWHEEL:
        window._wheel(ctypes.c_short((wparam >> 16) & 0xFFFF).value)
        return 0
    if msg == WM_GETOBJECT and (int(wparam) & 0xFFFFFFFF) == 0xFFFFFFFC:
        if window.msaa_enabled:
            try:
                from .msaa import lresult
                if window.msaa is None:
                    from .msaa import Accessible
                    window.msaa = Accessible(window)
                return lresult(window.msaa, int(wparam))
            except Exception:
                pass
    if msg == WM_GETOBJECT and (int(wparam) & 0xFFFFFFFF) in (
            (UIA_ROOT_OBJECT_ID & 0xFFFFFFFF), 0xFFFFFFFC):
        result = window._uia_getobject(wparam, lparam, hwnd)
        if result is not None:
            return result
    if msg == WM_IME_STARTCOMPOSITION:
        window._ime_start()
        return 0
    if msg == WM_IME_COMPOSITION:
        window._ime_composition(int(lparam))
        return 0
    if msg == WM_IME_ENDCOMPOSITION:
        window._ime_end()
        return 0
    if msg in (WM_POINTERDOWN, WM_POINTERUPDATE, WM_POINTERUP,
               WM_POINTERENTER, WM_POINTERLEAVE):
        window._pointer(msg, int(wparam))
        return 0
    if msg == WM_DPICHANGED:
        window._dpi_changed(int(wparam) & 0xFFFF, int(lparam))
        return 0
    if msg == WM_DROPFILES:
        window._drop_files(int(wparam))
        return 0
    if msg == WM_CLOSE:
        callback = getattr(window, "on_close", None)
        window.on_close = None
        if callback is not None:
            try:
                callback()
            except Exception:
                pass
        user32.DestroyWindow(hwnd)
        return 0
    if msg == WM_DESTROY:
        _windows.pop(int(hwnd), None)
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


def _register_class():
    global _class_registered, _window_proc
    if _class_registered:
        return
    _window_proc = WNDPROC(_wndproc)
    instance = kernel32.GetModuleHandleW(None)
    wc = WNDCLASSW()
    wc.style = CS_HREDRAW | CS_VREDRAW
    wc.lpfnWndProc = ctypes.cast(_window_proc, c_void_p)
    wc.hInstance = instance
    wc.hCursor = user32.LoadCursorW(None, IDC_ARROW)
    wc.hbrBackground = ctypes.c_void_p(COLOR_WINDOW + 1)
    wc.lpszClassName = _class_name
    if not user32.RegisterClassW(byref(wc)):
        raise ctypes.WinError(ctypes.get_last_error())
    _class_registered = True


def _proxy_proc(hwnd, msg, wparam, lparam):
    entry = _proxy_objects.get(int(hwnd))
    if entry is None:
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
    window, provider = entry
    if msg == WM_GETOBJECT and (int(wparam) & 0xFFFFFFFF) in (
            (UIA_ROOT_OBJECT_ID & 0xFFFFFFFF), 0xFFFFFFFC):
        try:
            from .uia_provider import uia
            uia.UiaReturnRawElementProvider.argtypes = [
                c_void_p, ctypes.c_size_t, ctypes.c_ssize_t, c_void_p]
            uia.UiaReturnRawElementProvider.restype = ctypes.c_ssize_t
            return uia.UiaReturnRawElementProvider(
                ctypes.c_void_p(hwnd), wparam, lparam, provider.simple)
        except Exception:
            return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


def _proxy_key_proc(hwnd, msg, wparam, lparam):
    entry = _proxy_key_objects.get(int(hwnd))
    if entry is None:
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
    window, old_proc = entry
    if msg == 0x0100 and int(wparam) == 0x09:  # WM_KEYDOWN, VK_TAB
        window._proxy_tab(bool(int(lparam) & 0x80000000))
        return 0
    return user32.CallWindowProcW(ctypes.c_void_p(old_proc),
                                  ctypes.c_void_p(hwnd), msg, wparam,
                                  lparam)


def _register_a11y():
    global _a11y_registered
    if _a11y_registered:
        return
    wc = WNDCLASSW()
    global _proxy_wndproc, _proxy_key_wndproc
    _proxy_wndproc = WNDPROC(_proxy_proc)
    _proxy_key_wndproc = WNDPROC(_proxy_key_proc)
    wc.lpfnWndProc = ctypes.cast(_proxy_wndproc, c_void_p)
    wc.hInstance = kernel32.GetModuleHandleW(None)
    wc.hbrBackground = ctypes.c_void_p(COLOR_WINDOW + 1)
    wc.lpszClassName = _a11y_class
    if not user32.RegisterClassW(byref(wc)):
        raise ctypes.WinError(ctypes.get_last_error())
    _a11y_registered = True


class Window:
    def __init__(self, title="AMFWX", width=800, height=600, theme=None):
        _register_class()
        self.title = title
        self.width = width
        self.height = height
        self.theme = get_theme(theme) if isinstance(theme, str) or theme is None \
            else theme
        self.root = Widget()
        self.root.parent = self
        self.layout = BoxLayout()
        self.pressed = None
        self.hovered = None
        self.focus_widget = None
        self.overlay = None
        self.drag_manager = None
        self.uia_enabled = False
        self.uia_provider = None
        self.msaa_enabled = False
        self.msaa = None
        self.on_close = None
        self._a11y_windows = {}
        self._a11y_by_handle = {}
        self._a11y_by_handle = {}
        self._proxy_updating = False
        self._accessibility_bridge = None
        self._uia_native = set()
        self._a11y_names = {}
        from .touch import GestureRecognizer

        self.gesture = GestureRecognizer()
        self.gesture.connect(self._on_gesture)
        self._gesture_target = None
        instance = kernel32.GetModuleHandleW(None)
        user32.CreateWindowExW.restype = ctypes.c_void_p
        user32.CreateWindowExW.argtypes = [
            ctypes.c_uint, c_wchar_p, c_wchar_p, ctypes.c_uint,
            c_int, c_int, c_int, c_int, c_void_p, c_void_p, c_void_p, c_void_p,
        ]
        self.hwnd = user32.CreateWindowExW(
            0, _class_name, title, WS_OVERLAPPEDWINDOW | WS_VISIBLE,
            CW_USEDEFAULT, CW_USEDEFAULT, width, height,
            None, None, instance, None,
        )
        if not self.hwnd:
            raise ctypes.WinError(ctypes.get_last_error())
        _windows[int(self.hwnd)] = self
        _register_a11y()
        import threading
        self.ui_thread = threading.get_ident()
        self._invoke_lock = threading.Lock()
        self._invoke_id = 0
        self._invoke_callbacks = {}
        self._invoke_results = {}
        shell32.DragAcceptFiles.argtypes = [c_void_p, ctypes.c_int]
        shell32.DragAcceptFiles(self.hwnd, 1)
        self.dpi = self._query_dpi()
        self.dpi_scale = self.dpi / 96.0
        self.physical_width = int(width * self.dpi_scale)
        self.physical_height = int(height * self.dpi_scale)
        self.canvas = Canvas(width, height, self.theme.background)
        user32.SetWindowPos.argtypes = [c_void_p, c_void_p, c_int, c_int,
                                        c_int, c_int, ctypes.c_uint]
        user32.SetWindowPos(self.hwnd, None, 0, 0, self.physical_width,
                            self.physical_height, 0x0002 | 0x0004)
        self._layout_root()
        user32.ShowWindow(self.hwnd, 1)
        user32.UpdateWindow(self.hwnd)

    def invoke(self, callback):
        import threading
        if threading.get_ident() == self.ui_thread:
            return callback()
        with self._invoke_lock:
            self._invoke_id += 1
            token = self._invoke_id
            self._invoke_callbacks[token] = callback
            user32.SendMessageW.argtypes = [c_void_p, ctypes.c_uint,
                                            ctypes.c_size_t, ctypes.c_ssize_t]
            user32.SendMessageW(ctypes.c_void_p(self.hwnd), WM_APP_INVOKE,
                                token, 0)
            error, result = self._invoke_results.pop(token, (None, None))
            self._invoke_callbacks.pop(token, None)
        if error is not None:
            raise error
        return result

    def _handle_invoke(self, token):
        callback = self._invoke_callbacks.get(token)
        if callback is None:
            return
        try:
            result = callback()
        except Exception as error:
            self._invoke_results[token] = (error, None)
        else:
            self._invoke_results[token] = (None, result)

    def geometry(self):
        rect = wintypes.RECT()
        user32.GetWindowRect.argtypes = [c_void_p, ctypes.POINTER(wintypes.RECT)]
        user32.GetWindowRect(ctypes.c_void_p(self.hwnd), byref(rect))
        return {"x": rect.left, "y": rect.top,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top}

    def restore_geometry(self, geometry):
        if not geometry:
            return False
        try:
            user32.SetWindowPos.argtypes = [c_void_p, c_void_p, c_int, c_int,
                                            c_int, c_int, ctypes.c_uint]
            user32.SetWindowPos(ctypes.c_void_p(self.hwnd), None,
                                int(geometry.get("x", 100)),
                                int(geometry.get("y", 100)),
                                int(geometry.get("width", self.physical_width)),
                                int(geometry.get("height", self.physical_height)),
                                0x0004)
            return True
        except Exception:
            return False

    def save_geometry(self, settings, key="window_geometry"):
        settings.set(key, self.geometry())
        return self

    def load_geometry(self, settings, key="window_geometry"):
        self.restore_geometry(settings.get(key))
        return self

    def enable_msaa(self):
        self.msaa_enabled = True
        if self.msaa is None:
            from .msaa import Accessible
            self.msaa = Accessible(self)
        return self

    def enable_uia(self):
        try:
            import ctypes
            ctypes.windll.ole32.CoInitializeEx(None, 2)
        except Exception:
            pass
        self.uia_enabled = True
        return self

    def _uia_value_changed(self, widget):
        if self.uia_provider is None:
            return
        found = self.uia_provider.root._find_widget(widget)
        if found is not None:
            from .uia_provider import UIA_ValueValuePropertyChangedEventId
            self.uia_provider.raise_event(UIA_ValueValuePropertyChangedEventId,
                                          found)

    def _uia_getobject(self, wparam=UIA_ROOT_OBJECT_ID, lparam=0, hwnd=None):
        if not self.uia_enabled:
            return None
        if self.uia_provider is None:
            from .uia_provider import UiaProvider
            self.uia_provider = UiaProvider(self)
        return self.uia_provider.handle_getobject(hwnd)

    def _dpi_changed(self, dpi, rect_pointer):
        self.dpi = int(dpi) or 96
        self.dpi_scale = self.dpi / 96.0
        try:
            rect = wintypes.RECT.from_address(rect_pointer)
            self.physical_width = rect.right - rect.left
            self.physical_height = rect.bottom - rect.top
            user32.SetWindowPos(self.hwnd, None, rect.left, rect.top,
                                self.physical_width, self.physical_height,
                                0x0004)
            self._resize(self.physical_width, self.physical_height)
            self.invalidate()
        except Exception:
            pass

    def _drop_files(self, drop_handle):
        try:
            count = shell32.DragQueryFileW(ctypes.c_void_p(drop_handle),
                                          0xFFFFFFFF, None, 0)
            paths = []
            for index in range(count):
                buffer = ctypes.create_unicode_buffer(2048)
                shell32.DragQueryFileW(ctypes.c_void_p(drop_handle), index,
                                      buffer, 2048)
                paths.append(buffer.value)
            point = wintypes.POINT()
            shell32.DragQueryPoint(ctypes.c_void_p(drop_handle), byref(point))
            shell32.DragFinish(ctypes.c_void_p(drop_handle))
            target = self._widget_at(int(point.x / self.dpi_scale),
                                     int(point.y / self.dpi_scale))
            if target is not None and hasattr(target, "drop_files"):
                target.drop_files(paths, point.x, point.y)
            else:
                self.files_dropped(paths)
        except Exception:
            pass

    def files_dropped(self, paths):
        return paths

    def _query_dpi(self):
        try:
            user32.GetDpiForWindow.argtypes = [c_void_p]
            user32.GetDpiForWindow.restype = ctypes.c_uint
            value = user32.GetDpiForWindow(self.hwnd)
            return int(value) if value else 96
        except Exception:
            return 96

    def scaled(self, value):
        return value * self.dpi_scale

    def add(self, widget, stretch=0):
        self.root.add(widget)
        self.layout.add(widget, stretch)
        self._layout_root()
        return widget

    def _layout_root(self):
        self.root.arrange(Rect(0, 0, self.canvas.width, self.canvas.height))
        self.layout.arrange(self.root, self.root.rect)
        self._sync_a11y()

    def _sync_a11y(self):
        if not hasattr(self, "_a11y_windows"):
            return
        stack = list(getattr(self.root, "children", []))
        while stack:
            widget = stack.pop()
            stack.extend(getattr(widget, "children", []))
            text = getattr(widget, "text", "")
            if callable(text):
                text = text()
            if not text:
                continue
            hwnd = self._a11y_windows.get(id(widget))
            if not hwnd:
                widget_type = type(widget).__name__
                extra = 0
                if widget_type == "Button":
                    class_name = "BUTTON"
                elif widget_type == "CheckBox":
                    class_name = "BUTTON"
                    extra = 0x00000003
                elif widget_type in ("LineEdit", "TextEdit"):
                    class_name = "EDIT"
                else:
                    class_name = "STATIC"
                hwnd = user32.CreateWindowExW(
                    0x00000020 | 0x00000080, class_name, str(text),
                    0x40000000 | 0x10000000 | extra | (0x00010000 if class_name in ("BUTTON", "EDIT") else 0), 0, 0, 1, 1,
                    ctypes.c_void_p(self.hwnd),
                    ctypes.c_void_p(1000 + (id(widget) & 0xFFFF)), None, None)
                if not hwnd:
                    continue
                from .uia_provider import Provider
                provider = Provider(self, widget)
                self._a11y_windows[id(widget)] = hwnd
                self._a11y_by_handle[int(hwnd)] = widget
                self._a11y_providers = getattr(self, "_a11y_providers", {})
                self._a11y_providers[int(hwnd)] = provider
                _proxy_objects[int(hwnd)] = (self, provider)
                user32.SetWindowLongPtrW.argtypes = [c_void_p, c_int,
                                                     c_void_p]
                user32.SetWindowLongPtrW.restype = c_void_p
                old_proc = user32.SetWindowLongPtrW(
                    ctypes.c_void_p(hwnd), -4,
                    ctypes.cast(_proxy_key_wndproc, c_void_p))
                _proxy_key_objects[int(hwnd)] = (self, old_proc)
                from .uia_native import attach as attach_uia, set_name as set_uia_name
                control_id = 1000 + (id(widget) & 0xFFFF)
                try:
                    attached = attach_uia(
                        hwnd, widget, text, control_id,
                        int(widget.rect.x), int(widget.rect.y),
                        max(1, int(widget.rect.w)), max(1, int(widget.rect.h)))
                    if attached:
                        self._uia_native.add(int(hwnd))
                except Exception:
                    pass
            user32.SetWindowTextW.argtypes = [c_void_p, c_wchar_p]
            self._proxy_updating = True
            user32.SetWindowTextW(ctypes.c_void_p(hwnd), str(text))
            if hasattr(self, "_uia_native") and int(hwnd) in self._uia_native:
                try:
                    from .uia_native import set_name as set_uia_name
                    set_uia_name(hwnd, text)
                except Exception:
                    pass
            if type(widget).__name__ == "CheckBox":
                user32.SendMessageW.argtypes = [c_void_p, ctypes.c_uint,
                                                ctypes.c_size_t,
                                                ctypes.c_ssize_t]
                user32.SendMessageW(ctypes.c_void_p(hwnd), 0x00F1,
                                    1 if getattr(widget, "checked", False) else 0,
                                    0)  # BM_SETCHECK
            self._proxy_updating = False
            user32.SetWindowPos(ctypes.c_void_p(hwnd), None,
                                int(widget.rect.x), int(widget.rect.y),
                                1, 1, 0x0004 | 0x0010)
        try:
            self.accessibility_bridge().sync()
        except Exception:
            pass

    def accessibility_bridge(self):
        if self._accessibility_bridge is None:
            from .accessibility import AccessibilityBridge
            self._accessibility_bridge = AccessibilityBridge(self)
        return self._accessibility_bridge

    def accessibility_tree(self):
        from .accessibility import AccessibilityTree
        return AccessibilityTree(self)

    def sync_accessibility(self):
        self._sync_a11y()

    def _proxy_tab(self, reverse=False):
        handles = [h for h in getattr(self, "_a11y_by_handle", {})]
        if not handles:
            return
        current = int(user32.GetFocus())
        try:
            index = handles.index(current)
        except ValueError:
            index = -1
        step = -1 if reverse else 1
        target = handles[(index + step) % len(handles)]
        user32.SetFocus(ctypes.c_void_p(target))
        self.accessibility_bridge().poll_focus()

    def _proxy_command(self, wparam, lparam):
        if getattr(self, "_proxy_updating", False):
            return
        notification = (wparam >> 16) & 0xFFFF
        handle = lparam & 0xFFFFFFFF
        widget = self._a11y_by_handle.get(handle)
        if widget is None:
            return
        if notification == 0:  # BN_CLICKED
            if type(widget).__name__ == "CheckBox" and hasattr(widget, "toggle"):
                widget.toggle()
            elif hasattr(widget, "activate"):
                widget.activate()
        elif notification == 0x0300:  # EN_CHANGE
            buffer = ctypes.create_unicode_buffer(2048)
            user32.GetWindowTextW.argtypes = [c_void_p, ctypes.c_wchar_p, c_int]
            user32.GetWindowTextW(ctypes.c_void_p(handle), buffer, 2048)
            setter = getattr(widget, "set_text", None)
            if setter is not None:
                self._proxy_updating = True
                try:
                    setter(buffer.value)
                finally:
                    self._proxy_updating = False
        self._accessibility_bridge = None

    def _destroy_a11y(self):
        try:
            from .uia_native import detach as detach_uia
            for hwnd in list(getattr(self, "_uia_native", set())):
                detach_uia(hwnd)
            self._uia_native = set()
        except Exception:
            pass
        for hwnd in list(getattr(self, "_a11y_providers", {})):
            _proxy_objects.pop(int(hwnd), None)
        self._a11y_providers = {}
        for hwnd in getattr(self, "_a11y_windows", {}).values():
            user32.DestroyWindow(ctypes.c_void_p(hwnd))
        self._a11y_windows = {}
        self._a11y_by_handle = {}
        self._a11y_by_handle = {}
        self._proxy_updating = False
        self._accessibility_bridge = None

    def _resize(self, width, height):
        self.physical_width, self.physical_height = width, height
        self.width = max(1, int(round(width / self.dpi_scale)))
        self.height = max(1, int(round(height / self.dpi_scale)))
        self.canvas.resize(self.width, self.height)
        self._layout_root()
        self.invalidate()

    def _paint(self):
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(self.hwnd, byref(ps))
        try:
            self.canvas.clear(self.theme.background)
            self.root.paint(self.canvas)
            if self.overlay is not None:
                self.overlay.paint(self.canvas)
            info = BITMAPINFO()
            info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            info.bmiHeader.biWidth = self.canvas.width
            info.bmiHeader.biHeight = -self.canvas.height
            info.bmiHeader.biPlanes = 1
            info.bmiHeader.biBitCount = 32
            info.bmiHeader.biCompression = 0
            buffer = (ctypes.c_ubyte * len(self.canvas.data)).from_buffer(
                self.canvas.data)
            gdi32.StretchDIBits(
                hdc, 0, 0, self.physical_width, self.physical_height,
                0, 0, self.canvas.width, self.canvas.height,
                ctypes.byref(buffer), byref(info), DIB_RGB_COLORS, SRCCOPY)
        finally:
            user32.EndPaint(self.hwnd, byref(ps))

    def _widget_at(self, x, y):
        if self.overlay is not None:
            found = self.overlay.hit_test(x, y)
            if found is not None:
                return found
        return self.root.hit_test(x, y)

    def set_overlay(self, widget):
        self.overlay = widget
        if widget is not None:
            widget.parent = self
        self.invalidate()
        return widget

    def close_overlay(self):
        self.overlay = None
        self.invalidate()

    def _context_menu(self, x, y):
        widget = self._widget_at(x, y)
        menu = None
        while widget is not None:
            menu = getattr(widget, "context_menu", None)
            if menu is not None:
                break
            widget = getattr(widget, "parent", None)
        if menu is None:
            return
        from .widgets import ContextMenu
        ContextMenu(menu).show_at(self, x, y)

    def _mouse_down(self, x, y):
        if self.overlay is not None and self.overlay.__class__.__name__ == "Tooltip":
            self.close_overlay()
        widget = self._widget_at(x, y)
        if self.overlay is not None:
            found = self.overlay.hit_test(x, y)
            if found is None and widget is not self.overlay:
                self.close_overlay()
        self.pressed = widget
        if widget is not None:
            if widget.focusable:
                self.set_focus(widget)
            widget.mouse_down(x, y)

    def _mouse_move(self, x, y):
        if self.drag_manager is not None and self.drag_manager.active:
            self.drag_manager.position = (x, y)
            return
        widget = self._widget_at(x, y)
        if self.hovered is not widget:
            if self.hovered is not None:
                self.hovered.hovered = False
            if widget is not None:
                widget.hovered = True
            self.hovered = widget
            self.invalidate()
        if widget is not None:
            widget.mouse_move(x, y)
        if self.pressed is not None:
            self.pressed.mouse_move(x, y)
        if widget is not None and getattr(widget, "tooltip_text", ""):
            if self.overlay is None or self.overlay.__class__.__name__ != "Tooltip":
                from .advanced import Tooltip
                tip = Tooltip(widget.tooltip_text)
                tip.enabled = False
                width = tip.size_hint()[0]
                tip.arrange(Rect(x + 12, y + 18, width, 28))
                self.set_overlay(tip)
        elif self.overlay is not None and self.overlay.__class__.__name__ == "Tooltip":
            self.close_overlay()

    def _mouse_up(self, x, y):
        if self.drag_manager is not None and self.drag_manager.active:
            self.drag_manager.finish(x, y)
            self.drag_manager = None
            self.pressed = None
            self.invalidate()
            return
        widget = self.pressed or self._widget_at(x, y)
        if widget is not None:
            widget.mouse_up(x, y)
        self.pressed = None
        self.invalidate()

    def _focusables(self, widget=None):
        widget = widget or self.root
        found = []
        if widget.focusable and widget.enabled and widget.visible:
            found.append(widget)
        for child in widget.children:
            found.extend(self._focusables(child))
        return found

    def set_focus(self, widget):
        if self.focus_widget is widget:
            return
        if self.focus_widget is not None:
            self.focus_widget.set_focused(False)
        self.focus_widget = widget
        if widget is not None:
            widget.set_focused(True)
        if self.uia_provider is not None and widget is not None:
            self.uia_provider.focus_event(widget)
        self.invalidate()

    def _modifiers(self):
        try:
            state = 0
            if user32.GetKeyState(0x10) & 0x8000:
                state |= 1
            if user32.GetKeyState(0x11) & 0x8000:
                state |= 2
            if user32.GetKeyState(0x12) & 0x8000:
                state |= 4
            return state
        except Exception:
            return 0

    def _key_down(self, key, modifiers=0):
        if key == 0x1B:
            user32.PostMessageW(self.hwnd, WM_CLOSE, 0, 0)
            return
        if key == 0x09:
            items = self._focusables()
            if items:
                index = items.index(self.focus_widget) if self.focus_widget in items else -1
                self.set_focus(items[(index + 1) % len(items)])
            return
        if self.focus_widget is not None:
            self.focus_widget.key_down(key, modifiers)
            self.invalidate()

    def _char_input(self, character):
        if self.focus_widget is not None:
            self.focus_widget.char_input(character)
            self.invalidate()

    def _wheel(self, delta):
        if self.focus_widget is not None:
            handler = getattr(self.focus_widget, "wheel", None)
            if handler:
                handler(delta)
                self.invalidate()

    def _ime_start(self):
        if self.focus_widget is not None:
            self.focus_widget.ime_start()
        self.invalidate()

    def _ime_composition(self, flags):
        if self.focus_widget is None:
            return
        try:
            imm32 = ctypes.WinDLL("imm32")
            imm32.ImmGetContext.argtypes = [c_void_p]
            imm32.ImmGetContext.restype = c_void_p
            imm32.ImmGetCompositionStringW.argtypes = [c_void_p, ctypes.c_uint,
                                                       c_void_p, ctypes.c_uint]
            imm32.ImmGetCompositionStringW.restype = ctypes.c_long
            imm32.ImmReleaseContext.argtypes = [c_void_p, c_void_p]
            context = imm32.ImmGetContext(self.hwnd)
            text = ""
            if context and flags & 0x8:
                length = imm32.ImmGetCompositionStringW(context, 0x8, None, 0)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length // 2 + 1)
                    imm32.ImmGetCompositionStringW(context, 0x8, buffer, length)
                    text = buffer.value
                imm32.ImmReleaseContext(self.hwnd, context)
            self.focus_widget.ime_composition(text, bool(flags & 0x800))
        except Exception:
            pass
        self.invalidate()

    def _ime_end(self):
        if self.focus_widget is not None:
            self.focus_widget.ime_end()
        self.invalidate()

    def _pointer(self, msg, wparam):
        try:
            info = POINTER_INFO()
            if not user32.GetPointerInfo(wparam & 0xFFFF, byref(info)):
                return
            point = wintypes.POINT(info.ptPixelLocation.x,
                                   info.ptPixelLocation.y)
            user32.ScreenToClient(self.hwnd, byref(point))
            if msg == WM_POINTERDOWN:
                user32.SetCapture(self.hwnd)
                state = "down"
            elif msg == WM_POINTERUP:
                user32.ReleaseCapture()
                state = "up"
            else:
                state = "move"
            self._touch(info.pointerId, int(point.x / self.dpi_scale), int(point.y / self.dpi_scale), state,
                        bool(info.pointerFlags & 0x2000))
        except Exception:
            pass

    def _touch(self, pointer_id, x, y, state="move", primary=False):
        from .touch import TouchEvent

        target = self._widget_at(x, y)
        if state == "down":
            self._gesture_target = target
            if target is not None and target.focusable:
                self.set_focus(target)
        event = TouchEvent(pointer_id, x, y, state, primary)
        if target is not None:
            target.touch_event(event)
        self.gesture.touch(pointer_id, x, y, state)
        self.invalidate()

    def _on_gesture(self, event):
        target = self._gesture_target
        if target is None:
            target = self._widget_at(event.x, event.y)
        if target is not None:
            target.gesture_event(event)
        self.invalidate()

    def set_theme(self, theme):
        self.theme = get_theme(theme) if isinstance(theme, str) else theme
        self.invalidate()
        return self

    def start_drag(self, data=None, source=None):
        from .dnd import DragManager

        self.drag_manager = DragManager(self)
        self.drag_manager.start(data, source)
        return self.drag_manager

    def invalidate(self):
        try:
            self._sync_a11y()
        except Exception:
            pass
        user32.InvalidateRect(self.hwnd, None, False)

    def render_to_png(self, path, scale=1):
        self._layout_root()
        self.canvas.clear(self.theme.background)
        self.root.paint(self.canvas)
        if self.overlay is not None:
            self.overlay.paint(self.canvas)
        target = self.canvas
        if scale and float(scale) != 1.0:
            target = self.canvas.scaled(int(self.canvas.width * scale),
                                        int(self.canvas.height * scale))
        return target.save_png(path)

    def render_to_pdf(self, path):
        self._layout_root()
        self.canvas.clear(self.theme.background)
        self.root.paint(self.canvas)
        if self.overlay is not None:
            self.overlay.paint(self.canvas)
        return self.canvas.save_pdf(path)

    def render_to_bmp(self, path):
        self._layout_root()
        self.canvas.clear(self.theme.background)
        self.root.paint(self.canvas)
        if self.overlay is not None:
            self.overlay.paint(self.canvas)
        return self.canvas.save_bmp(path)

    def process_events(self, max_ms=0):
        import time
        msg = wintypes.MSG()
        try:
            self.accessibility_bridge().poll_focus()
        except Exception:
            pass
        deadline = time.monotonic() + max_ms / 1000 if max_ms else None
        while True:
            has = user32.PeekMessageW(byref(msg), None, 0, 0, 1)
            if has:
                if msg.message == WM_QUIT:
                    return
                if (msg.message == WM_KEYDOWN and int(msg.wParam) == 0x09
                        and int(msg.hwnd) in getattr(self, "_a11y_by_handle", {})):
                    self._proxy_tab(bool(int(msg.lParam) & 0x80000000))
                    continue
                user32.IsDialogMessageW.argtypes = [c_void_p, ctypes.c_void_p]
                user32.IsDialogMessageW.restype = ctypes.c_bool
                if user32.IsDialogMessageW(ctypes.c_void_p(self.hwnd), byref(msg)):
                    continue
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageW(byref(msg))
                try:
                    self.accessibility_bridge().poll_focus()
                except Exception:
                    pass
            elif deadline is not None and time.monotonic() < deadline:
                time.sleep(0.001)
            else:
                break

    def run(self):
        self._layout_root()
        self._sync_a11y()
        msg = wintypes.MSG()
        while user32.GetMessageW(byref(msg), None, 0, 0) > 0:
            if (msg.message == WM_KEYDOWN and int(msg.wParam) == 0x09
                    and int(msg.hwnd) in getattr(self, "_a11y_by_handle", {})):
                self._proxy_tab(bool(int(msg.lParam) & 0x80000000))
                continue
            user32.IsDialogMessageW.argtypes = [c_void_p, ctypes.c_void_p]
            user32.IsDialogMessageW.restype = ctypes.c_bool
            if user32.IsDialogMessageW(ctypes.c_void_p(self.hwnd), byref(msg)):
                continue
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))
        return 0

    def close(self):
        user32.PostMessageW(self.hwnd, WM_CLOSE, 0, 0)
