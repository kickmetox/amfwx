"""Verify native DLL integrity against amfwx/bin/checksums.json."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "amfwx" / "bin"
MANIFEST = BIN / "checksums.json"


def verify():
    if not MANIFEST.exists():
        return ["Manifest fehlt: amfwx/bin/checksums.json"]
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    for name, expected in data.get("files", {}).items():
        path = BIN / name
        if not path.exists():
            errors.append(f"fehlt: {name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual.lower() != expected.lower():
            errors.append(f"Hash falsch: {name}")
    return errors


def main():
    errors = verify()
    for error in errors:
        print(f"FEHLER: {error}")
    if errors:
        return 1
    print(f"OK: {len(json.loads(MANIFEST.read_text(encoding='utf-8'))['files'])} DLLs verifiziert")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
