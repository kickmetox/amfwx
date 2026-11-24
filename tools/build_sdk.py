"""Build the SDK wheel including vendor/python32."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "amfwx" / "vendor" / "python32"


def main():
    source = ROOT / "vendor" / "python32"
    if not (source / "python.exe").is_file():
        raise SystemExit("vendor/python32 fehlt")
    if TARGET.exists():
        shutil.rmtree(TARGET)
    shutil.copytree(source, TARGET)
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "-w", str(ROOT / "dist"), "."],
            cwd=ROOT, check=True)
    finally:
        shutil.rmtree(TARGET, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
