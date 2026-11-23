"""Persistent home-device registry and adapter factory."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from .home import (FibaroHomeCenter, GenericHttpDevice, HomeError,
                   JaroliftBridge, ShellyDevice)


class HomeRegistry:
    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.devices = {}
        if self.path and self.path.is_file():
            self.load()

    def add(self, device, config=None):
        config = dict(config or {})
        host = getattr(device, "host", config.get("host", ""))
        port = int(getattr(device, "port", config.get("port", 80)) or 80)
        kind = getattr(device, "kind", config.get("kind", "generic"))
        name = getattr(device, "name", config.get("name", host))
        identifier = config.get("id") or str(uuid.uuid4())
        entry = {
            "id": identifier,
            "kind": kind,
            "name": name,
            "host": host,
            "port": port,
            "config": config,
        }
        self.devices[identifier] = entry
        return entry

    def add_discovered(self, device, **config):
        return self.add(device, config)

    def remove(self, identifier):
        return self.devices.pop(identifier, None)

    def adapter(self, identifier):
        entry = self.devices.get(identifier)
        if entry is None:
            raise HomeError("Gerät nicht gefunden")
        kind = entry["kind"]
        config = entry["config"]
        host = entry["host"]
        port = entry["port"]
        if kind == "shelly":
            return ShellyDevice(host, port)
        if kind == "fibaro":
            return FibaroHomeCenter(
                host, port, config.get("username", "admin"),
                config.get("password", "admin"), secure=config.get("secure", False))
        if kind == "jarolift":
            return JaroliftBridge(
                host, port, config.get("base_topic", "jarolift"),
                config.get("username"), config.get("password"))
        if kind in ("generic", "homepilot", "tahoma", "becker", "eve",
                    "seve", "ssdp"):
            base_url = config.get("base_url") or f"http://{host}:{port}"
            return GenericHttpDevice(
                base_url,
                status_path=config.get("status_path", "/status"),
                command_path=config.get("command_path", "/command"))
        raise HomeError(f"kein Adapter fuer {kind}")

    def save(self, path=None):
        target = Path(path) if path else self.path
        if target is None:
            raise HomeError("kein Registry-Pfad")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(list(self.devices.values()),
                                     indent=2, ensure_ascii=False),
                          encoding="utf-8")
        return target

    def load(self, path=None):
        source = Path(path) if path else self.path
        if source is None or not source.is_file():
            return self
        data = json.loads(source.read_text(encoding="utf-8"))
        self.devices = {entry["id"]: entry for entry in data}
        return self
