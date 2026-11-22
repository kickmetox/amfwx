"""Hardware diagnostic report for AMFWX."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from amfwx import DeviceManager


def pcan_available():
    import ctypes
    try:
        ctypes.WinDLL("PCANBasic.dll")
        return True
    except OSError:
        return False


def asyncua_available():
    return importlib.util.find_spec("asyncua") is not None


def build_report():
    manager = DeviceManager().refresh()
    summary = manager.summary()
    return {
        "devices": summary,
        "backends": {
            "serial": summary.get("serial", 0) > 0,
            "hid": summary.get("hid", 0) > 0,
            "raw_usb": summary.get("usb", 0) > 0,
            "bluetooth": summary.get("bluetooth", 0) > 0,
            "wlan": summary.get("wlan", 0) > 0,
            "displays": summary.get("displays", 0) > 0,
            "pcan": pcan_available(),
            "opcua": asyncua_available(),
        },
        "unsupported": ["firewire"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/hardware.json")
    args = parser.parse_args()
    report = build_report()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
