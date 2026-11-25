"""Named settings profiles for scanner/camera/print."""

from __future__ import annotations

import json
import os
from pathlib import Path


class ProfileError(RuntimeError):
    pass


def default_profile_path():
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / "AMFWX" / "profiles.json"


class ProfileStore:
    def __init__(self, path=None):
        self.path = Path(path) if path else default_profile_path()
        self.data = {}
        if self.path.is_file():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                self.data = {}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.data, indent=2),
                             encoding="utf-8")
        temporary.replace(self.path)

    def save(self, kind, name, values):
        name = str(name).strip()
        if not name:
            raise ProfileError("Profilname fehlt")
        self.data.setdefault(str(kind), {})[name] = dict(values)
        self._save()
        return name

    def load(self, kind, name):
        try:
            return dict(self.data[str(kind)][str(name)])
        except KeyError as error:
            raise ProfileError(f"Profil nicht gefunden: {name}") from error

    def names(self, kind):
        return sorted(self.data.get(str(kind), {}))

    def delete(self, kind, name):
        removed = self.data.get(str(kind), {}).pop(str(name), None)
        if removed is not None:
            self._save()
        return removed
