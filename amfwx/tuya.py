"""Tuya Cloud API client (signed requests)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from urllib.parse import quote

from .net import HttpClient, NetworkError


class TuyaError(RuntimeError):
    pass


class TuyaCloud:
    def __init__(self, access_id, access_secret, base_url="https://openapi.tuyaeu.com",
                 uid=None, timeout=15.0):
        self.access_id = str(access_id)
        self.access_secret = str(access_secret)
        self.base_url = str(base_url).rstrip("/")
        self.uid = str(uid) if uid else ""
        self.client = HttpClient(self.base_url, timeout=timeout)
        self.token = None
        self.token_expires = 0.0

    @staticmethod
    def _sha256(value):
        return hashlib.sha256(value).hexdigest()

    def _sign(self, method, path, body, timestamp, token=""):
        string_to_sign = (f"{method}\n{self._sha256(body)}\n\n{path}")
        payload = (self.access_id + timestamp + self.access_id +
                   string_to_sign)
        return hmac.new(self.access_secret.encode("utf-8"),
                        payload.encode("utf-8"),
                        hashlib.sha256).hexdigest().upper()

    def _request(self, method, path, body=b"", token=""):
        timestamp = str(int(time.time() * 1000))
        headers = {
            "client_id": self.access_id,
            "sign": self._sign(method, path, body, timestamp, token),
            "t": timestamp,
            "sign_method": "HMAC-SHA256",
        }
        if token:
            headers["access_token"] = token
        try:
            response = self.client.request(
                path, method=method, data=body, headers=headers)
        except NetworkError as error:
            raise TuyaError(str(error)) from error
        data = json.loads(response["body"].decode("utf-8", "replace"))
        if not data.get("success", False):
            raise TuyaError(str(data.get("msg", "Tuya-Fehler")))
        return data.get("result")

    def login(self):
        if self.token and time.time() < self.token_expires:
            return self.token
        result = self._request("GET", "/v1.0/token?grant_type=1")
        self.token = result.get("access_token")
        if not self.token:
            raise TuyaError("Tuya-Token fehlt")
        self.token_expires = time.time() + int(result.get("expire_time", 3600)) - 60
        return self.token

    def devices(self, uid=None):
        token = self.login()
        user = uid or self.uid
        if not user:
            raise TuyaError("Tuya-UID fehlt")
        return self._request("GET", f"/v1.0/users/{quote(user)}/devices",
                             token=token)

    def status(self, device_id):
        token = self.login()
        return self._request("GET", f"/v1.0/devices/{quote(device_id)}",
                             token=token)

    def send_commands(self, device_id, commands):
        token = self.login()
        body = json.dumps({"commands": commands}).encode("utf-8")
        return self._request("POST", f"/v1.0/devices/{quote(device_id)}/commands",
                             body=body, token=token)

    def switch(self, device_id, enabled, code="switch_1"):
        return self.send_commands(device_id, [{"code": code,
                                               "value": bool(enabled)}])
