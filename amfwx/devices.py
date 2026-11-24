"""Unified device inventory across AMFWX hardware interfaces."""

from __future__ import annotations

from .bluetooth import list_devices as list_bluetooth_devices
from .display import list_monitors
from .io.serial import list_ports
from .usb import list_hid_devices
from .usb_raw import list_usb_devices
from .wlan import list_interfaces as list_wlan_interfaces
from .twain import list_sources as list_twain_sources
from .naps2 import list_sources as list_naps2_sources
from .wia import list_wia_devices
from .network_scan import discover_network_devices
from .winprint import list_printers
from .camera import list_cameras, list_pnp_cameras


def _safe(collector):
    try:
        return collector()
    except Exception:
        return []


class DeviceManager:
    def __init__(self):
        self.snapshot = {}

    def refresh(self):
        self.snapshot = {
            "serial": _safe(list_ports),
            "hid": _safe(list_hid_devices),
            "usb": _safe(list_usb_devices),
            "bluetooth": _safe(lambda: list_bluetooth_devices(issue_inquiry=False)),
            "wlan": _safe(list_wlan_interfaces),
            "displays": _safe(list_monitors),
            "scanners": (_safe(list_wia_devices) +
                         _safe(list_twain_sources) +
                         _safe(list_naps2_sources)),
            "printers": _safe(list_printers),
            "cameras": (_safe(list_cameras) + _safe(list_pnp_cameras)),
            "network": _safe(lambda: discover_network_devices(timeout=0.2)),
        }
        return self

    def summary(self):
        if not self.snapshot:
            self.refresh()
        return {key: len(value) for key, value in self.snapshot.items()}

    def get(self, kind):
        if not self.snapshot:
            self.refresh()
        return self.snapshot.get(str(kind), [])


def list_devices():
    return DeviceManager().refresh().snapshot
