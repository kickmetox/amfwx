"""Optional hardware smoke report for CI and support."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _safe(function, default=None):
    try:
        return function()
    except Exception as error:
        return {"error": str(error)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/hardware-smoke.json")
    parser.add_argument("--timeout", type=float, default=1.0)
    args = parser.parse_args()
    from amfwx import (list_printers, list_pnp_cameras, naps2_available,
                       twain32)
    from amfwx.onvif import discover as onvif_discover
    from amfwx.tuya_discovery import discover as tuya_discover
    from amfwx.winprint import list_printers as windows_printers
    report = {
        "tools": {
            name: shutil.which(name) is not None
            for name in ("chip-tool", "gphoto2", "rtl_433", "NAPS2.Console.exe")
        },
        "twain32": twain32.available(),
        "naps2": naps2_available(),
        "printers": _safe(lambda: [item.name for item in list_printers()], []),
        "cameras": _safe(lambda: [item.name for item in list_pnp_cameras()], []),
        "onvif": _safe(lambda: onvif_discover(args.timeout), []),
        "tuya": _safe(lambda: tuya_discover(args.timeout), []),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
