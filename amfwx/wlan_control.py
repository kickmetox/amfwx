"""Windows WLAN control via netsh."""

from __future__ import annotations

import subprocess


class WlanControlError(RuntimeError):
    pass


def _run(command):
    process = subprocess.run(command, capture_output=True, text=True,
                             timeout=20)
    if process.returncode != 0:
        raise WlanControlError(process.stderr.strip() or
                               f"netsh exit {process.returncode}")
    return process.stdout


class WlanController:
    def __init__(self, runner=None):
        self.runner = runner or _run

    def interfaces(self):
        output = self.runner(["netsh", "wlan", "show", "interfaces"])
        result = []
        current = {}
        for line in output.splitlines():
            if ":" not in line:
                if current:
                    result.append(current)
                    current = {}
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key in ("name", "ssid", "state", "status", "signal",
                       "bssid"):
                current[key] = value
                if key == "name" and len(current) > 1:
                    result.append(current)
                    current = {"name": value}
        if current:
            result.append(current)
        return result

    def current(self):
        for interface in self.interfaces():
            if interface.get("ssid"):
                return interface
        return None

    def connect(self, ssid, profile=None, interface=None):
        name = profile or ssid
        command = ["netsh", "wlan", "connect", f"name={name}",
                   f"ssid={ssid}"]
        if interface:
            command.append(f"interface={interface}")
        return self.runner(command)

    def disconnect(self, interface=None):
        command = ["netsh", "wlan", "disconnect"]
        if interface:
            command.append(f"interface={interface}")
        return self.runner(command)

    def profiles(self):
        output = self.runner(["netsh", "wlan", "show", "profiles"])
        return [line.split(":", 1)[1].strip()
                for line in output.splitlines()
                if ":" in line and "profile" in line.lower()]

    def networks(self):
        output = self.runner(["netsh", "wlan", "show", "networks",
                              "mode=bssid"])
        result = []
        for line in output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                if key.strip().lower().startswith("ssid") and value.strip():
                    result.append(value.strip())
        return result
