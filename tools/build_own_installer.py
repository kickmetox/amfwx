"""Build the self-contained AMFWX installer."""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
APP = DIST / "AMFWX"
PAYLOAD = ROOT / "build" / "payload.zip"
VERSION = "3.17.0"


def build_payload():
    if not (APP / "AMFWX.exe").exists():
        raise SystemExit("dist/AMFWX/AMFWX.exe fehlt: tools/build_app.ps1 ausführen")
    PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(PAYLOAD, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in APP.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(APP))


def build_installer():
    build_payload()
    work = ROOT / "build" / "own_installer"
    spec = ROOT / "build" / "own_installer.spec"
    for path in (work, spec):
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile", "--windowed",
        "--name", "AMFWX-Setup",
        "--distpath", str(DIST / "own"),
        "--workpath", str(work),
        "--specpath", str(ROOT / "build"),
        "--add-data", f"{PAYLOAD};.",
        "--paths", str(ROOT),
        str(ROOT / "installer" / "own_installer.py"),
    ]
    subprocess.run(command, check=True, cwd=ROOT)
    produced = DIST / "own" / "AMFWX-Setup.exe"
    target = DIST / f"AMFWX-Own-Setup-{VERSION}.exe"
    if produced.exists():
        produced.replace(target)
    return target


if __name__ == "__main__":
    print(build_installer())
