"""Crash logging for AMFWX."""

from __future__ import annotations

import os
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path


def default_log_path():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    return base / "AMFWX" / "crash.log"


class CrashLogger:
    def __init__(self, path=None, max_bytes=1024 * 1024):
        self.path = Path(path) if path else default_log_path()
        self.max_bytes = max(4096, int(max_bytes))
        self._lock = threading.Lock()
        self._previous = None

    def log(self, exception, context=""):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            if self.path.exists() and self.path.stat().st_size > self.max_bytes:
                backup = self.path.with_suffix(".old")
                try:
                    if backup.exists():
                        backup.unlink()
                    self.path.replace(backup)
                except OSError:
                    pass
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(f"[{datetime.now().isoformat()}]\n")
                if context:
                    handle.write(f"context: {context}\n")
                handle.write("".join(traceback.format_exception(
                    type(exception), exception, exception.__traceback__)))
                handle.write("\n")
        return self.path

    def install(self):
        self._previous = sys.excepthook
        logger = self

        def hook(kind, value, tb):
            if value is not None:
                value.__traceback__ = tb
                logger.log(value, "unhandled")
            if logger._previous is not None:
                logger._previous(kind, value, tb)

        sys.excepthook = hook
        return self

    def uninstall(self):
        if self._previous is not None:
            sys.excepthook = self._previous
            self._previous = None
        return self
