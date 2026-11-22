"""Security helpers: native DLL integrity and safe resource names."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class SecurityError(RuntimeError):
    pass


def _defaults():
    root = Path(__file__).resolve().parent
    return root / "bin", root / "bin" / "checksums.json"


def verify_native_dlls(bin_dir=None, manifest_path=None, strict=False):
    """Check native DLL hashes against the shipped manifest.

    Returns a dict with ``ok``, ``missing`` and ``mismatched`` lists.
    With ``strict=True`` a mismatch raises SecurityError instead.
    """
    default_bin, default_manifest = _defaults()
    bin_dir = Path(bin_dir) if bin_dir is not None else default_bin
    manifest_path = Path(manifest_path) if manifest_path is not None else (
        bin_dir / "checksums.json")
    if not manifest_path.exists():
        result = {"ok": False, "missing": ["checksums.json"],
                  "mismatched": []}
    else:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        missing = []
        mismatched = []
        for name, expected in data.get("files", {}).items():
            path = bin_dir / name
            if not path.exists():
                missing.append(name)
                continue
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual.lower() != expected.lower():
                mismatched.append(name)
        result = {"ok": not missing and not mismatched,
                  "missing": missing, "mismatched": mismatched}
    if strict and not result["ok"]:
        raise SecurityError(
            f"native DLL integrity failed: missing={result['missing']} "
            f"mismatched={result['mismatched']}")
    return result


def safe_resource_name(name):
    """Reject ZIP member names that could escape the archive root."""
    text = str(name).replace("\\", "/")
    if not text or text.startswith("/") or text.startswith("\\"):
        raise SecurityError(f"unsafe resource name: {name!r}")
    if ":" in text.split("/")[0]:
        raise SecurityError(f"unsafe drive path: {name!r}")
    parts = [part for part in text.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        raise SecurityError(f"path traversal: {name!r}")
    return "/".join(parts)


def safe_join(root, name):
    root = Path(root).resolve()
    target = (root / safe_resource_name(name)).resolve()
    if root != target and root not in target.parents:
        raise SecurityError(f"path escapes root: {name!r}")
    return target
