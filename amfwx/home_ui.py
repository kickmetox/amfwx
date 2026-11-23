"""Discovery panel and add-to-registry window."""

from __future__ import annotations

import threading

from .home_discovery import discover_home
from .home_registry import HomeRegistry
from .quick import HStack, Stack, Text
from .widgets import BoxLayout, Button, Label, Widget
from .window import Window


class HomeDevicesPanel(Stack):
    def __init__(self, registry, on_added=None):
        super().__init__("vertical", spacing=6, padding=10)
        self.registry = registry
        self.on_added = on_added
        self.devices = []
        self.rows = Stack("vertical", spacing=4, padding=0)
        self.saved = Stack("vertical", spacing=4, padding=0)
        self.status = Label("Noch keine Suche.")
        self.add(Text("Gefundene Geräte"))
        self.add(self.rows)
        self.add(Text("Gespeicherte Ger\u00e4te"))
        self.add(self.saved)
        self.add(self.status)
        self.refresh_saved()

    def set_devices(self, devices):
        self.devices = list(devices)
        self.rows.children.clear()
        self.rows.layout.items.clear()
        if not self.devices:
            self.rows.add(Label("Keine Geräte gefunden."))
        for device in self.devices:
            self.rows.add(self._row(device))
        self.status.text = f"{len(self.devices)} Gerät(e) gefunden."
        return self

    def _row(self, device):
        name = getattr(device, "name", "?")
        kind = getattr(device, "kind", "?")
        host = getattr(device, "host", "")
        button = Button("Hinzufügen",
                        on_click=lambda: self.add_device(device))
        return HStack(Label(f"{name}  [{kind}]  {host}"), button)

    def add_device(self, device):
        entry = self.registry.add_discovered(device)
        self.status.text = f"Hinzugefügt: {entry['name']}"
        if self.on_added is not None:
            self.on_added(entry)
        return entry

    def refresh_saved(self):
        self.saved.children.clear()
        self.saved.layout.items.clear()
        for entry in self.registry.devices.values():
            button = Button("Entfernen",
                            on_click=lambda value=entry["id"]: self.remove_device(value))
            self.saved.add(HStack(Label(f"{entry['name']}  [{entry['kind']}]  {entry['host']}"), button))
        if not self.registry.devices:
            self.saved.add(Label("Noch nichts gespeichert."))
        return self

    def remove_device(self, identifier):
        entry = self.registry.remove(identifier)
        self.status.text = "Entfernt." if entry else "Nicht gefunden."
        self.refresh_saved()
        return entry


class HomeDevicesWindow(Window):
    def __init__(self, registry=None):
        super().__init__("AMFWX Geräte", 760, 520)
        self.registry = registry or HomeRegistry()
        self.panel = HomeDevicesPanel(self.registry)
        self.scan_button = Button("Netzwerk durchsuchen", on_click=self.scan)
        self.close_button = Button("Schließen", on_click=self.close)
        self.layout = BoxLayout("vertical", spacing=8, padding=12)
        self.root.children.clear()
        self.layout.items.clear()
        for widget in (self.panel, HStack(self.scan_button,
                                          self.close_button)):
            self.root.add(widget)
            self.layout.add(widget)
        self._layout_root()
        self.invalidate()

    def scan(self):
        self.scan_button.enabled = False
        self.panel.status.text = "Suche läuft..."
        self.invalidate()

        def work():
            try:
                devices = discover_home(timeout=4.0)
            except Exception as error:
                devices = []
                message = f"Fehler: {error}"
            else:
                message = None
            self.invoke(lambda: self._done(devices, message))

        threading.Thread(target=work, daemon=True).start()

    def _done(self, devices, message):
        self.scan_button.enabled = True
        self.panel.set_devices(devices)
        if message:
            self.panel.status.text = message
        self.invalidate()
