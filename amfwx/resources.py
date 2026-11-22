"""ZIP resource packs for AMFWX (themes, icons, translations)."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


class ResourcePack:
    def __init__(self, path):
        self.path = Path(path)
        self.archive = zipfile.ZipFile(self.path)
        self._names = set(self.archive.namelist())

    def names(self):
        return sorted(self._names)

    def read(self, name):
        from .security import safe_resource_name
        return self.archive.read(safe_resource_name(name))

    def text(self, name, encoding="utf-8"):
        return self.read(name).decode(encoding)

    def json(self, name):
        return json.loads(self.text(name))

    def exists(self, name):
        from .security import safe_resource_name
        return safe_resource_name(name) in self._names

    def png(self, name):
        from .canvas import Canvas
        return Canvas.from_png(self.read(name))

    def close(self):
        self.archive.close()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
