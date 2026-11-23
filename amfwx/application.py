"""Small application lifecycle and command-line handling."""

from __future__ import annotations

import sys

from .single_instance import SingleInstance
from .window import Window


class AppConfig:
    def __init__(self, title="AMFWX", width=800, height=600, theme="dark",
                 single=True, show_version=False, help=False,
                 doctor=False, devices=False, registry=None,
                 list_devices=False, device_action=None, device=None,
                 scan_printers=None, scan_host=None, scan_dir=None,
                 scan_source="Platen", scan_pages=1, scan_port=9096,
                 scan_http=False, scan_pdf=None, scan_ui=False,
                 list_printers=False, print_file=None, printer=None,
                 scan_print=None):
        self.title = str(title)
        self.width = int(width)
        self.height = int(height)
        self.theme = str(theme)
        self.single = bool(single)
        self.show_version = bool(show_version)
        self.help = bool(help)
        self.doctor = bool(doctor)
        self.devices = bool(devices)
        self.registry = registry
        self.list_devices = bool(list_devices)
        self.device_action = device_action
        self.device = device
        self.scan_printers = scan_printers
        self.scan_host = scan_host
        self.scan_dir = scan_dir
        self.scan_source = scan_source
        self.scan_pages = int(scan_pages)
        self.scan_port = int(scan_port)
        self.scan_http = bool(scan_http)
        self.scan_pdf = scan_pdf
        self.scan_ui = bool(scan_ui)
        self.list_printers = bool(list_printers)
        self.print_file = print_file
        self.printer = printer
        self.scan_print = scan_print

    @classmethod
    def parse(cls, argv=None):
        args = list(sys.argv[1:] if argv is None else argv)
        config = cls()
        index = 0
        while index < len(args):
            value = args[index]
            if value == "--version":
                config.show_version = True
            elif value in ("-h", "--help"):
                config.help = True
            elif value == "--doctor":
                config.doctor = True
            elif value == "--devices":
                config.devices = True
            elif value == "--registry" and index + 1 < len(args):
                index += 1
                config.registry = args[index]
            elif value == "--list-devices":
                config.list_devices = True
            elif value == "--device" and index + 1 < len(args):
                index += 1
                config.device = args[index]
            elif value == "--action" and index + 1 < len(args):
                index += 1
                config.device_action = args[index]
            elif value == "--scan-printers" and index + 1 < len(args):
                index += 1
                config.scan_printers = args[index]
            elif value == "--scan-host" and index + 1 < len(args):
                index += 1
                config.scan_host = args[index]
            elif value == "--scan-dir" and index + 1 < len(args):
                index += 1
                config.scan_dir = args[index]
            elif value == "--scan-source" and index + 1 < len(args):
                index += 1
                config.scan_source = args[index]
            elif value == "--scan-pages" and index + 1 < len(args):
                index += 1
                config.scan_pages = int(args[index])
            elif value == "--scan-port" and index + 1 < len(args):
                index += 1
                config.scan_port = int(args[index])
            elif value == "--scan-http":
                config.scan_http = True
            elif value == "--scan-pdf" and index + 1 < len(args):
                index += 1
                config.scan_pdf = args[index]
            elif value == "--scan-ui":
                config.scan_ui = True
            elif value == "--list-printers":
                config.list_printers = True
            elif value == "--print-file" and index + 1 < len(args):
                index += 1
                config.print_file = args[index]
            elif value == "--printer" and index + 1 < len(args):
                index += 1
                config.printer = args[index]
            elif value == "--scan-print" and index + 1 < len(args):
                index += 1
                config.scan_print = args[index]
            elif value == "--no-single":
                config.single = False
            elif value == "--theme" and index + 1 < len(args):
                index += 1
                config.theme = args[index]
            elif value == "--title" and index + 1 < len(args):
                index += 1
                config.title = args[index]
            index += 1
        return config

    def usage(self):
        return ("AMFWX application\n\n"
                "  --version       Version anzeigen\n"
                "  --theme NAME    Theme (dark, light, high_contrast)\n"
                "  --title TEXT    Fenstertitel\n"
                "  --no-single     Mehrfachstart erlauben\n"
                "  --doctor        Hardware-Diagnose\n"
                "  --devices       Geräte-Discovery öffnen\n"
                "  --registry PATH Registry-JSON\n"
                "  --list-devices  Gespeicherte Geräte anzeigen\n"
                "  --device NAME   Gerät für --action\n"
                "  --action NAME   open/close/on/off\n"
                "  --scan-printers CIDR  eSCL/IPP im LAN suchen\n"
                "  --scan-host HOST  eSCL-Scan starten\n"
                "  --scan-dir DIR    Zielordner (Default: Dokumente/AMFWX Scans)\n"
                "  --scan-source SRC Platen oder Feeder\n"
                "  --scan-pages N    Anzahl Seiten\n"
                "  --scan-port PORT  9096 HTTPS / 9095 HTTP\n"
                "  --scan-http       HTTP statt HTTPS\n"
                "  --scan-pdf PATH   Scan als mehrseitiges PDF speichern\n"
                "  --scan-ui         Scan-Fenster oeffnen\n"
                "  --list-printers   Windows-Drucker anzeigen\n"
                "  --print-file PATH Datei an Drucker senden\n"
                "  --printer NAME    Ziel-Drucker\n"
                "  --scan-print NAME Scan direkt drucken\n"
                "  -h, --help      Hilfe anzeigen\n")


class Application:
    def __init__(self, config=None, window_factory=None, name="AMFWX"):
        self.config = config or AppConfig()
        self.window_factory = window_factory or self._default_window
        self.name = name
        self.window = None
        self.lock = SingleInstance(name, on_activate=self.activate)

    def _default_window(self):
        return Window(self.config.title, self.config.width,
                      self.config.height, self.config.theme)

    def _device_command(self):
        from .home_registry import HomeRegistry
        registry = HomeRegistry(self.config.registry)
        if self.config.list_devices:
            for entry in registry.devices.values():
                print(f"{entry['id']}  {entry['kind']}  {entry['name']}  "
                      f"{entry['host']}:{entry['port']}")
            return 0
        action = (self.config.device_action or "").lower()
        if action not in ("open", "close", "on", "off"):
            print("--action muss open, close, on oder off sein")
            return 2
        target = None
        for entry in registry.devices.values():
            if entry["id"] == self.config.device or entry["name"] == self.config.device:
                target = entry
                break
        if target is None:
            print("Gerät nicht gefunden")
            return 2
        adapter = registry.adapter(target["id"])
        method = {"open": "open_cover", "close": "close_cover",
                  "on": "on", "off": "off"}[action]
        result = getattr(adapter, method)()
        print(result if result is not None else "ok")
        return 0

    def _scan_command(self):
        from .escl import EsclScanner
        scanner = EsclScanner(self.config.scan_host, self.config.scan_port,
                              secure=not self.config.scan_http, timeout=90)
        temporary = None
        try:
            if self.config.scan_print:
                import tempfile
                from .scan_pdf import scan_to_pdf
                from .winprint import print_file
                if self.config.scan_pdf:
                    target = self.config.scan_pdf
                else:
                    handle = tempfile.NamedTemporaryFile(
                        suffix=".pdf", prefix="amfwx_print_", delete=False)
                    handle.close()
                    target = handle.name
                    temporary = target
                filename = scan_to_pdf(scanner, target,
                                       source=self.config.scan_source,
                                       max_pages=self.config.scan_pages)
                job = print_file(filename, self.config.scan_print,
                                "AMFWX Scan")
                print(filename)
                print(f"Druckauftrag gesendet: {job}")
                return 0
            if self.config.scan_pdf:
                from .scan_pdf import scan_to_pdf
                filename = scan_to_pdf(scanner, self.config.scan_pdf,
                                       source=self.config.scan_source,
                                       max_pages=self.config.scan_pages)
                print(filename)
                return 0
            from .scan_transfer import scan_to_folder
            files = scan_to_folder(scanner, self.config.scan_dir,
                                   source=self.config.scan_source,
                                   max_pages=self.config.scan_pages)
        except Exception as error:
            print(f"Scan fehlgeschlagen: {error}")
            return 1
        finally:
            if temporary:
                try:
                    import os
                    os.unlink(temporary)
                except OSError:
                    pass
        for filename in files:
            print(filename)
        return 0

    def activate(self):

        if self.window is not None:
            import ctypes
            user32 = ctypes.windll.user32
            user32.ShowWindow(self.window.hwnd, 1)
            user32.SetForegroundWindow(self.window.hwnd)

    def run(self):
        if self.config.help:
            print(self.config.usage())
            return 0
        if self.config.show_version:
            from . import __version__
            print(f"AMFWX {__version__}")
            return 0
        if self.config.doctor:
            from .diagnostics import diagnostics, format_diagnostics
            print(format_diagnostics(diagnostics()))
            return 0
        if self.config.list_printers:
            from .winprint import list_printers
            for item in list_printers():
                print(item.name)
            return 0
        if self.config.print_file:
            from .winprint import print_file
            if not self.config.printer:
                print("--printer fehlt")
                return 2
            try:
                job = print_file(self.config.print_file, self.config.printer)
            except Exception as error:
                print(f"Druck fehlgeschlagen: {error}")
                return 1
            print(f"Druckjob {job}")
            return 0
        if self.config.scan_ui:
            from .scan_ui import ScanWindow
            self.window = ScanWindow()
            return self.window.run()
        if self.config.scan_host:
            return self._scan_command()
        if self.config.scan_printers:
            from .print_discovery import scan_network
            for endpoint in scan_network(self.config.scan_printers):
                print(f"{endpoint.host}:{endpoint.port} escl={endpoint.escl}")
            return 0
        if self.config.single and not self.lock.acquire():
            return 0
        if self.config.list_devices or self.config.device_action:
            try:
                return self._device_command()
            finally:
                self.lock.release()
        if self.config.devices:
            from .home_registry import HomeRegistry
            from .home_ui import HomeDevicesWindow
            try:
                self.window = HomeDevicesWindow(HomeRegistry(self.config.registry))
                return self.window.run()
            finally:
                if self.window is not None:
                    self.window.close()
                self.lock.release()
        try:
            self.window = self.window_factory()
            return self.window.run()
        finally:
            if self.window is not None:
                self.window.close()
            self.lock.release()
