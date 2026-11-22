"""Small JSON settings store for AMFWX applications."""

from __future__ import annotations

import json
import os
from pathlib import Path


def default_path():
    base = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "AMFWX" / "settings.json"
    return Path.home() / ".amfwx" / "settings.json"


class Settings:
    def __init__(self, path=None):
        self.path = Path(path) if path else default_path()
        self.values = {}
        self.load()

    def load(self):
        try:
            self.values = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.values = {}
        return self

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.values, indent=2,
                                            ensure_ascii=False),
                                 encoding="utf-8")
            temporary.replace(self.path)
            return True
        except OSError:
            return False

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value, save=True):
        self.values[key] = value
        if save:
            self.save()
        return value

    def add_recent(self, path, limit=10):
        items = [item for item in self.get("recent_files", [])
                 if item != str(path)]
        items.insert(0, str(path))
        self.set("recent_files", items[:limit])
        return items[:limit]

    def recent(self):
        return list(self.get("recent_files", []))
