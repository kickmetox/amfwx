"""Small plugin registry for AMFWX."""

from __future__ import annotations

import importlib


class PluginError(RuntimeError):
    pass


class Plugin:
    name = "plugin"
    version = "0.0"

    def activate(self, app=None):
        return self

    def deactivate(self):
        return None


class PluginRegistry:
    def __init__(self):
        self.plugins = {}

    def register(self, plugin):
        name = getattr(plugin, "name", "")
        if not name:
            raise PluginError("Plugin ohne Namen")
        if name in self.plugins:
            raise PluginError(f"Plugin bereits registriert: {name}")
        self.plugins[name] = plugin
        return plugin

    def unregister(self, name):
        plugin = self.plugins.pop(name, None)
        if plugin is not None:
            try:
                plugin.deactivate()
            except Exception:
                pass
        return plugin

    def get(self, name):
        return self.plugins.get(name)

    def names(self):
        return sorted(self.plugins)

    def activate_all(self, app=None):
        for name in self.names():
            self.plugins[name].activate(app)
        return self

    def deactivate_all(self):
        for name in reversed(self.names()):
            self.unregister(name)
        return self

    def load_module(self, module_name, register=None):
        module = importlib.import_module(module_name)
        plugin = getattr(module, "PLUGIN", None)
        if plugin is None and callable(register):
            plugin = register(module)
        if plugin is None:
            raise PluginError(f"Modul ohne PLUGIN: {module_name}")
        return self.register(plugin)
