"""Unified AMFWX dashboard."""

from __future__ import annotations

import threading

from .camera import list_cameras, list_pnp_cameras
from .devices import DeviceManager
from .quick import HStack
from .widgets import (BoxLayout, Button, ComboBox, FilePicker, Label,
                      ListBox)
from .window import Window
from .winprint import list_printers


class DashboardWindow(Window):
    def __init__(self):
        super().__init__("AMFWX Zentrale", 820, 560)
        self.manager = DeviceManager()
        self.category = ComboBox([
            "Scanner", "Drucker", "Kameras", "Netzwerk", "USB",
            "Schnittstellen", "Alle",
        ], 6, on_change=lambda _value: self.on_category())
        self.items = ListBox()
        self.summary = Label("Lade Geräte...")
        self.print_file = FilePicker("", filters=[("PDF", "*.pdf")])
        self.scanner_button = Button("Scanner", on_click=self.open_scanner)
        self.camera_button = Button("Kamera", on_click=self.open_camera)
        self.print_button = Button("Druckvorschau", on_click=self.open_print)
        self.status = Label("Bereit.")
        self.refresh_button = Button("Aktualisieren", on_click=self.refresh,
                                     variant="primary")
        self.close_button = Button("Schließen", on_click=self.close)
        self.layout = BoxLayout("vertical", spacing=6, padding=12)
        self.root.children.clear()
        self.layout.items.clear()
        for row in [
            HStack(Label("Kategorie"), self.category, self.refresh_button),
            HStack(self.scanner_button, self.camera_button, self.print_button),
            self.print_file,
            self.summary,
            self.items,
            self.status,
            HStack(self.close_button),
        ]:
            self.root.add(row)
            self.layout.add(row)
        self._layout_root()
        self.invalidate()
        self.refresh()

    def refresh(self):
        self.status.text = "Geräte werden gesucht..."
        self.invalidate()

        def work():
            try:
                self.manager.refresh()
                printers = [printer.name for printer in list_printers()]
                cameras = [camera.name for camera in list_cameras()]
                cameras += [camera.name for camera in list_pnp_cameras()]
                data = dict(self.manager.snapshot)
                data["printers"] = printers
                data["cameras"] = cameras
            except Exception as error:
                self.invoke(lambda: self._done({}, str(error)))
            else:
                self.invoke(lambda: self._done(data, None))

        threading.Thread(target=work, daemon=True).start()

    def _done(self, data, error):
        if error:
            self.status.text = f"Fehler: {error}"
        else:
            self.data = data
            summary = {key: len(value) for key, value in data.items()}
            self.summary.text = " · ".join(
                f"{key}: {value}" for key, value in summary.items())
            self._populate()
            self.status.text = "Aktualisiert."
        self.invalidate()

    def _populate(self):
        data = getattr(self, "data", {})
        category = self.category.current_text()
        if category == "Alle":
            items = []
            for key, values in data.items():
                for value in values:
                    items.append(f"{key}: {value}")
        else:
            key = {"Scanner": "scanners", "Drucker": "printers",
                   "Kameras": "cameras", "Netzwerk": "network",
                   "USB": "usb", "Schnittstellen": "serial"}.get(
                       category, category.lower())
            items = [str(value) for value in data.get(key, [])]
        self.items.set_items(items)

    def open_scanner(self):
        from .scanner_ui import ScannerWindow
        window = ScannerWindow()
        window.run()

    def open_camera(self):
        from .camera_ui import CameraWindow
        window = CameraWindow()
        window.run()

    def open_print(self):
        path = self.print_file.path
        if not path:
            self.status.text = "Keine PDF gewählt."
            self.invalidate()
            return
        from .print_ui import PrintPreviewWindow
        window = PrintPreviewWindow(path)
        window.run()

    def on_category(self):
        self._populate()
        self.invalidate()
