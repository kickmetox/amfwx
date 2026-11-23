"""Somfy TaHoma / Connexoon local API client."""

from __future__ import annotations

import ssl
from urllib.parse import quote

from .net import HttpClient, NetworkError

BASE_PATH = "/enduser-mobile-web/1/enduserAPI"


class TahomaError(RuntimeError):
    pass


class Tahoma:
    def __init__(self, host, token, port=8443, secure=True, timeout=10.0,
                 verify_tls=False):
        self.host = str(host)
        self.port = int(port)
        self.token = str(token)
        scheme = "https" if secure else "http"
        context = None
        if secure and not verify_tls:
            context = ssl._create_unverified_context()
        self.client = HttpClient(
            f"{scheme}://{self.host}:{self.port}{BASE_PATH}",
            timeout=timeout,
            headers={"Authorization": f"Bearer {self.token}"},
            ssl_context=context)

    def setup(self):
        try:
            return self.client.json("/setup")
        except NetworkError as error:
            raise TahomaError(str(error)) from error

    def devices(self):
        return self.setup().get("devices", [])

    def states(self, device_url):
        try:
            return self.client.json(
                f"/setup/devices/{quote(device_url, safe='')}/states")
        except NetworkError as error:
            raise TahomaError(str(error)) from error

    def execute(self, device_url, command, parameters=None, label="AMFWX"):
        action = {"deviceURL": device_url,
                  "commands": [{"name": str(command),
                                "parameters": list(parameters or [])}]}
        try:
            return self.client.json(
                "/exec/apply", method="POST",
                json_data={"label": label, "actions": [action]})
        except NetworkError as error:
            raise TahomaError(str(error)) from error

    def open_cover(self, device_url):
        return self.execute(device_url, "open")

    def close_cover(self, device_url):
        return self.execute(device_url, "close")

    def stop_cover(self, device_url):
        return self.execute(device_url, "stop")

    def set_position(self, device_url, position):
        return self.execute(device_url, "setClosure",
                            [max(0, min(100, int(position)))])

    def set_temperature(self, device_url, temperature):
        return self.execute(device_url, "setTemperature",
                            [float(temperature)])
