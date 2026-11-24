"""AMFWX update check against GitHub releases."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

API = "https://api.github.com/repos/kickmetox/amfwx/releases/latest"


class UpdateError(RuntimeError):
    pass


def parse_version(value):
    parts = []
    for item in str(value).strip().lstrip("v").split("."):
        digits = "".join(ch for ch in item if ch.isdigit())
        parts.append(int(digits or 0))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def is_newer(latest, current):
    return parse_version(latest) > parse_version(current)


def release_info(api=API, timeout=15.0):
    request = urllib.request.Request(
        api, headers={"User-Agent": "AMFWX-update-check",
                      "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=float(timeout)) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        raise UpdateError(str(error)) from error
    return {
        "tag": data.get("tag_name", ""),
        "name": data.get("name", ""),
        "url": data.get("html_url", ""),
        "published": data.get("published_at", ""),
        "assets": [{"name": item.get("name", ""),
                    "url": item.get("browser_download_url", ""),
                    "size": item.get("size", 0)}
                   for item in data.get("assets", [])],
    }


def check(current, api=API, timeout=15.0):
    release = release_info(api, timeout)
    release["current"] = str(current)
    release["newer"] = is_newer(release["tag"], current)
    return release


def pick_installer(assets):
    for asset in assets:
        name = str(asset.get("name", "")).lower()
        if name.endswith(".exe") and "setup" in name:
            return asset.get("url", "")
    return ""


def download_update(asset_url, target):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(asset_url, target)
    except Exception as error:
        raise UpdateError(str(error)) from error
    return str(target)
