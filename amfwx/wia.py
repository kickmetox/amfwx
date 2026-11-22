"""Optional WIA scanner enumeration via COM automation."""

from __future__ import annotations


class WiaDevice:
    def __init__(self, device_id, name, kind):
        self.device_id = device_id
        self.name = name
        self.kind = kind

    def __repr__(self):
        return f"WiaDevice({self.name!r}, {self.kind!r})"


def list_wia_devices():
    try:
        import comtypes.client
    except ImportError:
        return []
    try:
        manager = comtypes.client.CreateObject("WIA.DeviceManager")
    except Exception:
        return []
    devices = []
    try:
        infos = manager.DeviceInfos
        for index in range(1, infos.Count + 1):
            info = infos.Item(index)
            try:
                name = str(info.Properties("Name").Value)
            except Exception:
                name = ""
            try:
                kind = str(info.Properties("Type").Value)
            except Exception:
                kind = ""
            devices.append(WiaDevice(str(info.DeviceID), name, kind))
    except Exception:
        return []
    return devices
