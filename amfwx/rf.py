"""Optional 433 MHz RF discovery through rtl_433."""

from __future__ import annotations

import json
import shutil
import subprocess


class RfError(RuntimeError):
    pass


def available():
    return shutil.which("rtl_433") is not None


def discover(seconds=10, runner=None, protocols=None):
    if not available() and runner is None:
        return []
    command = ["rtl_433", "-F", "json", "-T", str(int(seconds))]
    process = (runner or subprocess.run)(command, capture_output=True,
                                         text=True, timeout=int(seconds) + 30)
    devices = []
    for line in (process.stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            item = json.loads(line)
        except ValueError:
            continue
        model = str(item.get("model", ""))
        if protocols and not any(name.lower() in model.lower()
                                 for name in protocols):
            continue
        devices.append(item)
    return devices


def jarolift_devices(seconds=10, runner=None):
    return discover(seconds, runner, ("jarolift", "becker", "centronic"))


def summary(device):
    return {
        "model": device.get("model", ""),
        "id": device.get("id", device.get("device_id", "")),
        "channel": device.get("channel", ""),
        "command": device.get("command", ""),
        "rssi": device.get("rssi", ""),
    }
