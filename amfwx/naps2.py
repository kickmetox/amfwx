"""32-bit TWAIN/WIA scanner access through NAPS2.Console.exe."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class Naps2Error(RuntimeError):
    pass


class Naps2Source:
    def __init__(self, driver, name):
        self.driver = str(driver)
        self.name = str(name)

    @property
    def id(self):
        return f"{self.driver}:{self.name}"

    def __repr__(self):
        return f"Naps2Source({self.driver!r}, {self.name!r})"


def find_naps2():
    candidates = [
        os.environ.get("AMFWX_NAPS2", ""),
        shutil.which("NAPS2.Console.exe") or "",
        shutil.which("NAPS2.Console") or "",
    ]
    roots = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
        Path(__file__).resolve().parent.parent / "vendor" / "naps2",
    ]
    for root in roots:
        if not str(root):
            continue
        candidates.append(str(root / "NAPS2" / "NAPS2.Console.exe"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return ""


def available():
    return bool(find_naps2())


class Naps2Scanner:
    def __init__(self, exe=None, runner=None, timeout=180):
        self.exe = exe or find_naps2()
        self.runner = runner or subprocess.run
        self.timeout = int(timeout)
        if not self.exe and runner is None:
            raise Naps2Error("NAPS2.Console.exe fehlt")

    def _run(self, arguments):
        process = self.runner([self.exe] + arguments, capture_output=True,
                              text=True, timeout=self.timeout)
        return process

    def list_sources(self):
        sources = []
        for driver in ("wia", "twain"):
            try:
                process = self._run(["--listdevices", "--driver", driver])
            except Exception:
                continue
            for line in (process.stdout or "").splitlines():
                name = line.strip()
                if name:
                    sources.append(Naps2Source(driver, name))
        return sources

    def scan(self, source, path, dpi=300, paper_source="Glass"):
        if isinstance(source, Naps2Source):
            driver, name = source.driver, source.name
        else:
            driver, _, name = str(source).partition(":")
        if not driver or not name:
            raise Naps2Error("ungueltige NAPS2-Quelle")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        process = self._run([
            "-o", str(target), "--driver", driver, "--device", name,
            "--dpi", str(int(dpi)), "--source", str(paper_source),
        ])
        if process.returncode != 0 or not target.is_file():
            raise Naps2Error((process.stderr or "").strip() or
                             "NAPS2-Scan fehlgeschlagen")
        return str(target)


def list_sources():
    try:
        return Naps2Scanner().list_sources()
    except Naps2Error:
        return []
