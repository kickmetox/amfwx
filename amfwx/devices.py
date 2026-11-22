"""Unified device inventory across AMFWX hardware interfaces."""

from __future__ import annotations

from .bluetooth import list_devices as list_bluetooth_devices
from .display import list_monitors
from .io.serial import list_ports
from .usb import list_hid_devices
from .usb_raw import list_usb_devices
from .wlan import list_interfaces as list_wlan_interfaces


class DeviceManager:
    def __init__(self):
        self.snapshot = {}

    def refresh(self):
        self.snapshot = {
            "serial": list_ports(),
            "hid": list_hid_devices(),
            "usb": list_usb_devices(),
            "bluetooth": list_bluetooth_devices(issue_inquiry=False),
            "wlan": list_wlan_interfaces(),
            "displays": list_monitors(),
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
