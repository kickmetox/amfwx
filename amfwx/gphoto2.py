"""Optional gPhoto2 CLI adapter for DSLR tethering."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class GPhoto2Error(RuntimeError):
    pass


def available():
    return shutil.which("gphoto2") is not None


def list_cameras(runner=None):
    runner = runner or subprocess.run
    if shutil.which("gphoto2") is None and runner is subprocess.run:
        return []
    process = runner(["gphoto2", "--auto-detect"], capture_output=True,
                     text=True, timeout=20)
    cameras = []
    for line in (process.stdout or "").splitlines():
        line = line.strip()
        if not line or line.startswith("-") or line.lower().startswith("model"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            cameras.append({"model": parts[0], "port": parts[-1]})
    return cameras


class GPhoto2Camera:
    def __init__(self, port=None, runner=None):
        if not available() and runner is None:
            raise GPhoto2Error("gphoto2 fehlt")
        self.port = port
        self.runner = runner or subprocess.run

    def _run(self, arguments, timeout=120):
        command = ["gphoto2"]
        if self.port:
            command += ["--port", self.port]
        command += arguments
        process = self.runner(command, capture_output=True, text=True,
                              timeout=timeout)
        if process.returncode != 0:
            raise GPhoto2Error(process.stderr.strip() or
                               f"gphoto2 exit {process.returncode}")
        return process.stdout

    def settings(self):
        return self._run(["--list-config"])

    def capture(self, directory, filename=None):
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / (filename or "capture_%Y%m%d_%H%M%S.%C")
        self._run(["--capture-image-and-download", "--force-overwrite",
                   "--filename", str(target)])
        return str(target)
