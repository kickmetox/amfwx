"""Generate a small SBOM for AMFWX."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "amfwx" / "bin"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    binaries = []
    for path in sorted(BIN.glob("*.dll")):
        binaries.append({"name": path.name, "sha256": digest(path),
                         "size": path.stat().st_size})
    licenses = []
    for path in sorted(BIN.glob("LICENSE-*")):
        licenses.append({"name": path.name, "sha256": digest(path)})
    return {
        "bomFormat": "AMFWX-SBOM",
        "specVersion": "1.0",
        "metadata": {
            "component": "amfwx",
            "version": "3.11.0",
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        },
        "native": binaries,
        "licenses": licenses,
        "pythonDependencies": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/sbom.json")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
