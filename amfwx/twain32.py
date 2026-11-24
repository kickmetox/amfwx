"""32-bit TWAIN bridge for 32-bit-only scanner drivers."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


class Twain32Error(RuntimeError):
    pass


class Twain32Source:
    def __init__(self, identifier, name, manufacturer):
        self.id = int(identifier)
        self.name = name
        self.product_name = name
        self.manufacturer = manufacturer

    def __repr__(self):
        return f"Twain32Source({self.name!r}, {self.manufacturer!r})"


def helper_path():
    return Path(__file__).resolve().parent / "twain32_helper.py"


def python32_path():
    candidates = [
        os.environ.get("AMFWX_PYTHON32", ""),
        str(Path(__file__).resolve().parent.parent / "vendor" / "python32" /
            "python.exe"),
        str(Path(__file__).resolve().parent / "vendor" / "python32" /
            "python.exe"),
        r"C:\Python312-32\python.exe",
        r"C:\Python311-32\python.exe",
        r"C:\Python310-32\python.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return ""


def available():
    return bool(python32_path()) and helper_path().is_file()


def _run(arguments, timeout=180):
    python = python32_path()
    if not python:
        raise Twain32Error("kein 32-Bit-Python gefunden "
                           "(AMFWX_PYTHON32 setzen)")
    process = subprocess.run([python, str(helper_path())] + arguments,
                             capture_output=True, text=True, timeout=timeout)
    output = (process.stdout or "").strip().splitlines()
    if not output:
        raise Twain32Error(process.stderr.strip() or "keine Ausgabe")
    try:
        data = json.loads(output[-1])
    except ValueError as error:
        raise Twain32Error(output[-1]) from error
    if "error" in data:
        raise Twain32Error(data["error"])
    return data


def list_sources():
    if not available():
        return []
    data = _run(["--list"], timeout=30)
    return [Twain32Source(item.get("id", 0), item.get("name", ""),
                          item.get("manufacturer", ""))
            for item in data.get("sources", [])]


def scan(source, path, show_ui=False, timeout=180):
    if not available():
        raise Twain32Error("32-Bit-TWAIN-Bruecke nicht verfuegbar")
    arguments = ["--scan", "--source", str(source), "--path", str(path)]
    if show_ui:
        arguments.append("--ui")
    return _run(arguments, timeout=timeout).get("path", str(path))
