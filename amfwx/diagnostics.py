"""Hardware diagnostics for CLI and support."""

from __future__ import annotations

import json
import platform
import struct


def _safe(function, default=None):
    try:
        return function()
    except Exception as error:
        return default if default is not None else {"error": str(error)}


def diagnostics(timeout=0.5):
    from . import list_twain32_sources, list_twain_sources, list_wia_devices
    from .network_scan import discover_network_devices
    from .twain32 import available as twain32_available
    from .twain32 import python32_path

    def sources():
        return [{"name": source.name, "manufacturer": source.manufacturer}
                for source in list_twain_sources()]

    def wia():
        return [{"name": device.name, "id": device.device_id}
                for device in list_wia_devices()]

    def twain32():
        return [{"name": source.name, "manufacturer": source.manufacturer}
                for source in list_twain32_sources()]

    def network():
        return [{"kind": device.kind, "name": device.name,
                 "address": device.address, "port": device.port}
                for device in discover_network_devices(timeout=timeout)]

    return {
        "version": __import__("amfwx").__version__,
        "python": platform.python_version(),
        "bits": struct.calcsize("P") * 8,
        "twain64": _safe(sources, []),
        "twain32": {
            "available": bool(twain32_available()),
            "python": python32_path(),
            "sources": _safe(twain32, []),
        },
        "wia": _safe(wia, []),
        "network": _safe(network, []),
    }


def format_diagnostics(data):
    return json.dumps(data, indent=2, ensure_ascii=False)
