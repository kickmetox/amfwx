"""Zigbee control through the deCONZ REST API."""

from __future__ import annotations

from .net import HttpClient, NetworkError


class ZigbeeError(RuntimeError):
    pass


class DeconzClient:
    def __init__(self, host="127.0.0.1", port=80, api_key="", timeout=10.0,
                 secure=False):
        self.host = str(host)
        self.port = int(port)
        self.api_key = str(api_key)
        scheme = "https" if secure else "http"
        self.client = HttpClient(f"{scheme}://{self.host}:{self.port}",
                                 timeout=timeout)

    def _path(self, suffix=""):
        return f"/api/{self.api_key}{suffix}"

    def lights(self):
        try:
            return self.client.json(self._path("/lights"))
        except NetworkError as error:
            raise ZigbeeError(str(error)) from error

    def sensors(self):
        try:
            return self.client.json(self._path("/sensors"))
        except NetworkError as error:
            raise ZigbeeError(str(error)) from error

    def light(self, identifier):
        try:
            return self.client.json(self._path(f"/lights/{identifier}"))
        except NetworkError as error:
            raise ZigbeeError(str(error)) from error

    def set_light(self, identifier, **state):
        payload = {"on": bool(state.pop("on", True))}
        payload.update(state)
        try:
            return self.client.json(
                self._path(f"/lights/{identifier}/state"),
                method="PUT", json_data=payload)
        except NetworkError as error:
            raise ZigbeeError(str(error)) from error

    def on(self, identifier, **state):
        return self.set_light(identifier, on=True, **state)

    def off(self, identifier):
        return self.set_light(identifier, on=False)
