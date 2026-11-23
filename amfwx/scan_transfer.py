"""Persist scanned pages to a local destination folder."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def default_scan_dir():
    base = os.environ.get("USERPROFILE") or str(Path.home())
    return Path(base) / "Documents" / "AMFWX Scans"


def _unique(target):
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    index = 1
    while True:
        candidate = target.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def transfer_files(paths, destination=None):
    folder = Path(destination) if destination else default_scan_dir()
    folder.mkdir(parents=True, exist_ok=True)
    result = []
    for source in paths:
        source = Path(source)
        target = _unique(folder / source.name)
        shutil.copy2(source, target)
        result.append(str(target))
    return result


def scan_to_folder(scanner, destination=None, prefix="scan", source="Platen",
                   max_pages=1, **kwargs):
    folder = Path(destination) if destination else default_scan_dir()
    folder.mkdir(parents=True, exist_ok=True)
    if int(max_pages) <= 1:
        return [scanner.scan(str(_unique(folder / f"{prefix}.jpg")),
                             source=source, **kwargs)]
    return scanner.scan_pages(str(folder), prefix=prefix, source=source,
                              max_pages=max_pages, **kwargs)
