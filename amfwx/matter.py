"""Matter commissioning through an optional chip-tool binary."""

from __future__ import annotations

import shutil
import subprocess


class MatterError(RuntimeError):
    pass


def find_chip_tool():
    return shutil.which("chip-tool") or ""


def available():
    return bool(find_chip_tool())


class MatterController:
    def __init__(self, chip_tool=None, runner=None):
        self.chip_tool = chip_tool or find_chip_tool()
        self.runner = runner or subprocess.run
        if not self.chip_tool and runner is None:
            raise MatterError("chip-tool fehlt")

    def _run(self, arguments, timeout=120):
        process = self.runner([self.chip_tool] + arguments,
                              capture_output=True, text=True,
                              timeout=timeout)
        if process.returncode != 0:
            raise MatterError(process.stderr.strip() or
                              f"chip-tool exit {process.returncode}")
        return process.stdout

    def commission(self, node_id, setup_code):
        return self._run(["pairing", "code", str(int(node_id)),
                          str(setup_code)])

    def on(self, node_id, endpoint=1):
        return self._run(["onoff", "on", str(int(node_id)),
                          str(int(endpoint))])

    def off(self, node_id, endpoint=1):
        return self._run(["onoff", "off", str(int(node_id)),
                          str(int(endpoint))])

    def toggle(self, node_id, endpoint=1):
        return self._run(["onoff", "toggle", str(int(node_id)),
                          str(int(endpoint))])

    def read_onoff(self, node_id, endpoint=1):
        return self._run(["onoff", "read", "on-off", str(int(node_id)),
                          str(int(endpoint))])

    def level(self, node_id, percent, endpoint=1):
        value = max(0, min(254, int(round(int(percent) * 254 / 100))))
        return self._run(["levelcontrol", "move-to-level", str(value),
                          "0", "0", "0", str(int(node_id)),
                          str(int(endpoint))])

    def color_temperature(self, node_id, mireds, endpoint=1):
        return self._run(["colorcontrol", "move-to-color-temperature",
                          str(int(mireds)), "0", "0", "0",
                          str(int(node_id)), str(int(endpoint))])
