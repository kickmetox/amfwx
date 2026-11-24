"""LLM-callable UI tools for AMFWX sessions."""

from __future__ import annotations

import base64
import json
import os
import tempfile

from .canvas import Rect
from .widgets import (Button, CheckBox, ComboBox, Label, LineEdit, ListBox,
                      ProgressBar, RadioButton, Slider, SpinBox, Widget)
from .textedit import TextEdit
from .window import Window


KIND_MAP = {
    "label": Label,
    "button": Button,
    "line_edit": LineEdit,
    "text_edit": TextEdit,
    "checkbox": CheckBox,
    "slider": Slider,
    "combo": ComboBox,
    "progress": ProgressBar,
    "radio": RadioButton,
    "spin": SpinBox,
    "list": ListBox,
}


class UiSession:
    """A UI session that a language model can manipulate through tools."""

    def __init__(self, theme="dark"):
        self.theme = theme
        self.window = None
        self.widgets = {}
        self._next_id = 1
        self.allow_app_actions = False

    def create_window(self, title="AMFWX", width=640, height=480,
                      theme=None):
        self.close()
        self.window = Window(str(title), int(width), int(height),
                             theme=theme or self.theme)
        self.widgets = {}
        self._next_id = 1
        self.allow_app_actions = False
        self.window._layout_root()
        return {"ok": True, "window": str(title),
                "width": int(width), "height": int(height)}

    def _require_window(self):
        if self.window is None:
            raise RuntimeError("kein Fenster; zuerst create_window")
        return self.window

    def _new_id(self):
        result = f"w{self._next_id}"
        self._next_id += 1
        return result

    def add_widget(self, kind, text="", x=12, y=12, width=180, height=32,
                   parent=None, items=None):
        window = self._require_window()
        key = str(kind).lower()
        if key not in KIND_MAP:
            raise ValueError(f"unbekannter Widget-Typ: {kind}")
        cls = KIND_MAP[key]
        if key == "combo":
            widget = cls(items=list(items or ["A", "B"]))
        else:
            widget = cls(str(text))
        if key == "slider":
            widget = Slider(0, 100, int(text or 0))
        elif key == "progress":
            widget = ProgressBar(int(text or 0))
        elif key == "spin":
            widget = SpinBox(int(text or 0))
        elif key == "list":
            widget = ListBox([item.strip() for item in str(text).split(",") if item.strip()])
        target = self.widgets.get(parent) if parent else None
        container = target if isinstance(target, Widget) else window.root
        container.add(widget)
        widget.arrange(Rect(int(x), int(y), int(width), int(height)))
        widget_id = self._new_id()
        self.widgets[widget_id] = widget
        window.invalidate()
        return {"ok": True, "id": widget_id, "kind": key}

    def set_widget_text(self, widget_id, text):
        widget = self.widgets.get(str(widget_id))
        if widget is None:
            raise KeyError(f"unbekanntes Widget: {widget_id}")
        if hasattr(widget, "set_text"):
            widget.set_text(str(text))
        elif hasattr(widget, "text"):
            widget.text = str(text)
        if self.window is not None:
            self.window.invalidate()
        return {"ok": True, "id": str(widget_id), "text": str(text)}

    def click(self, widget_id):
        widget = self.widgets.get(str(widget_id))
        if widget is None:
            raise KeyError(f"unbekanntes Widget: {widget_id}")
        if hasattr(widget, "activate"):
            widget.activate()
        elif hasattr(widget, "toggle"):
            widget.toggle()
        elif hasattr(widget, "mouse_up"):
            widget.mouse_up(0, 0)
        return {"ok": True, "id": str(widget_id)}

    def list_widgets(self):
        result = []
        for widget_id, widget in self.widgets.items():
            result.append({
                "id": widget_id,
                "kind": type(widget).__name__,
                "text": str(getattr(widget, "text", "")),
                "x": int(widget.rect.x), "y": int(widget.rect.y),
                "width": int(widget.rect.w), "height": int(widget.rect.h),
            })
        return result

    def snapshot(self, path=None):
        window = self._require_window()
        if path is None:
            path = os.path.join(tempfile.gettempdir(),
                                "amfwx_sdk_snapshot.png")
        window.render_to_png(str(path))
        return {"ok": True, "path": str(path)}

    def snapshot_base64(self):
        window = self._require_window()
        handle, path = tempfile.mkstemp(suffix=".png")
        os.close(handle)
        try:
            window.render_to_png(path)
            with open(path, "rb") as file:
                data = base64.b64encode(file.read()).decode("ascii")
            return {"ok": True, "format": "png", "base64": data}
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def run(self):
        window = self._require_window()
        return window.run()

    def close(self):
        if self.window is not None:
            self.window.close()
            self.window.process_events(40)
            self.window = None
            self.widgets = {}


def _tool(name, description, properties, required=()):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(required),
            },
        },
    }


APP_TOOL_SPECS = [
    _tool("list_devices", "List scanners, printers, cameras and interfaces.", {}),
    _tool("scan_document", "Scan via eSCL to a PDF.",
          {"host": {"type": "string"}, "source": {"type": "string"},
           "pages": {"type": "integer"}, "output": {"type": "string"}},
          ["host", "output"]),
    _tool("print_file", "Print a file through the Windows queue.",
          {"path": {"type": "string"}, "printer": {"type": "string"},
           "copies": {"type": "integer"}, "duplex": {"type": "boolean"}},
          ["path", "printer"]),
    _tool("camera_snapshot", "Capture one webcam/IP camera frame.",
          {"path": {"type": "string"}, "index": {"type": "integer"},
           "url": {"type": "string"}}, ["path"]),
]

TOOL_SPECS = APP_TOOL_SPECS + [
    _tool("create_window", "Create or replace the application window.",
          {"title": {"type": "string"},
           "width": {"type": "integer"},
           "height": {"type": "integer"},
           "theme": {"type": "string"}}, ["title"]),
    _tool("add_widget", "Add a widget to the window.",
          {"kind": {"type": "string",
                    "enum": sorted(KIND_MAP)},
           "text": {"type": "string"},
           "x": {"type": "integer"}, "y": {"type": "integer"},
           "width": {"type": "integer"},
           "height": {"type": "integer"},
           "parent": {"type": "string"}}, ["kind"]),
    _tool("set_widget_text", "Change the text of a widget.",
          {"id": {"type": "string"}, "text": {"type": "string"}},
          ["id", "text"]),
    _tool("click", "Activate a button or toggle a checkbox.",
          {"id": {"type": "string"}}, ["id"]),
    _tool("list_widgets", "List all widgets with ids and geometry.", {}),
    _tool("snapshot", "Render the current window to a PNG file.",
          {"path": {"type": "string"}}),
    _tool("snapshot_base64", "Render the current window as base64 PNG.", {}),
]


def call_tool(session, name, arguments):
    arguments = dict(arguments or {})
    try:
        if name == "create_window":
            return session.create_window(**arguments)
        if name == "add_widget":
            return session.add_widget(**arguments)
        if name == "set_widget_text":
            return session.set_widget_text(arguments["id"],
                                           arguments["text"])
        if name == "click":
            return session.click(arguments["id"])
        if name == "list_widgets":
            return {"ok": True, "widgets": session.list_widgets()}
        if name == "snapshot":
            return session.snapshot(arguments.get("path"))
        if name in ("list_devices", "scan_document", "print_file",
                    "camera_snapshot"):
            if not getattr(session, "allow_app_actions", False):
                return {"ok": False,
                        "error": "App-Aktionen sind deaktiviert"}
            if name == "list_devices":
                from .devices import DeviceManager
                return {"ok": True, "devices": DeviceManager().refresh().summary()}
            if name == "scan_document":
                from .escl import EsclScanner
                from .scan_pdf import scan_to_pdf
                scanner = EsclScanner(arguments["host"])
                return {"ok": True, "path": scan_to_pdf(
                    scanner, arguments["output"],
                    source=arguments.get("source", "Platen"),
                    max_pages=int(arguments.get("pages", 1)))}
            if name == "print_file":
                from .winprint import print_file
                return {"ok": True, "job": print_file(
                    arguments["path"], arguments["printer"],
                    copies=int(arguments.get("copies", 1)),
                    duplex=bool(arguments.get("duplex", False)))}
            if name == "camera_snapshot":
                from .camera import Webcam
                from .ipcam import IpCamera
                camera = (IpCamera(arguments["url"])
                          if arguments.get("url") else
                          Webcam(int(arguments.get("index", 0))))
                try:
                    camera.read().save(arguments["path"])
                finally:
                    camera.close()
                return {"ok": True, "path": arguments["path"]}
        if name == "snapshot_base64":
            return session.snapshot_base64()
        return {"ok": False, "error": f"unbekanntes Tool: {name}"}
    except Exception as error:
        return {"ok": False, "error": str(error)}


def tool_result_text(result):
    return json.dumps(result, ensure_ascii=False)
