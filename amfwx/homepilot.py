"""Rademacher HomePilot local REST API client."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from urllib.parse import urlencode


class HomePilotError(RuntimeError):
    pass


POS_UP_CMD = "POS_UP_CMD"
POS_DOWN_CMD = "POS_DOWN_CMD"
STOP_CMD = "STOP_CMD"
GOTO_POS_CMD = "GOTO_POS_CMD"
TURN_ON_CMD = "TURN_ON_CMD"
TURN_OFF_CMD = "TURN_OFF_CMD"
TARGET_TEMPERATURE_CFG = "TARGET_TEMPERATURE_CFG"


class HomePilot:
    def __init__(self, host, password="", api_version=1, timeout=10.0):
        self.host = str(host).rstrip("/")
        self.password = str(password)
        self.api_version = int(api_version)
        self.base_path = "/hp" if self.api_version >= 2 else ""
        self.timeout = float(timeout)
        self.cookies = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies))
        self.authenticated = False

    @property
    def base_url(self):
        return f"http://{self.host}{self.base_path}"

    def _json(self, path, method="GET", payload=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.base_url + path, data=data, method=method, headers=headers)
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                body = response.read()
        except urllib.error.HTTPError as error:
            raise HomePilotError(f"HTTP {error.code}") from error
        except OSError as error:
            raise HomePilotError(str(error)) from error
        try:
            return json.loads(body.decode("utf-8", "replace"))
        except ValueError as error:
            raise HomePilotError("ungueltige JSON-Antwort") from error

    def login(self):
        if self.authenticated or not self.password:
            return False
        salt_response = self._json("/authentication/password_salt",
                                   method="POST")
        salt = salt_response.get("password_salt", "")
        first = hashlib.sha256(self.password.encode("utf-8")).hexdigest()
        salted = hashlib.sha256(f"{salt}{first}".encode("utf-8")).hexdigest()
        response = self._json("/authentication/login", method="POST",
                              payload={"password": salted,
                                       "password_salt": salt})
        if response.get("error_code", 0) != 0:
            raise HomePilotError(response.get("error_message", "Login fehlgeschlagen"))
        self.authenticated = True
        return True

    def devices(self):
        return self._json("/devices").get("payload", {}).get("devices", [])

    def states(self):
        result = {}
        for kind, key in (("Actuator", "devices"), ("Sensor", "meters"),
                          ("Transmitter", "transmitters")):
            data = self._json(f"/v4/devices?devtype={kind}")
            for device in data.get(key, []) or []:
                result[str(device.get("did"))] = device
        return result

    def _command(self, did, name, value=None):
        payload = {"name": name}
        if value is not None:
            payload["value"] = value
        return self._json(f"/devices/{did}", method="PUT", payload=payload)

    def open_cover(self, did):
        return self._command(did, POS_UP_CMD)

    def close_cover(self, did):
        return self._command(did, POS_DOWN_CMD)

    def stop_cover(self, did):
        return self._command(did, STOP_CMD)

    def set_position(self, did, position):
        return self._command(did, GOTO_POS_CMD, max(0, min(100, int(position))))

    def turn_on(self, did):
        return self._command(did, TURN_ON_CMD)

    def turn_off(self, did):
        return self._command(did, TURN_OFF_CMD)

    def set_temperature(self, did, temperature):
        return self._command(did, TARGET_TEMPERATURE_CFG, float(temperature))
