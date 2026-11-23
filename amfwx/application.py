"""Small application lifecycle and command-line handling."""

from __future__ import annotations

import sys

from .single_instance import SingleInstance
from .window import Window


class AppConfig:
    def __init__(self, title="AMFWX", width=800, height=600, theme="dark",
                 single=True, show_version=False, help=False,
                 doctor=False, devices=False, registry=None):
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
        if self.config.single and not self.lock.acquire():
            return 0
        if self.config.devices:
            from .home_registry import HomeRegistry
            from .home_ui import HomeDevicesWindow
            self.window = HomeDevicesWindow(HomeRegistry(self.config.registry))
            return self.window.run()
        try:
            self.window = self.window_factory()
            return self.window.run()
        finally:
            if self.window is not None:
                self.window.close()
            self.lock.release()
