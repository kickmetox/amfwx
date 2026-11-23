"""AVM FRITZ!Box TR-064 client (hosts, WLAN, login)."""

from __future__ import annotations

import hashlib
import re
import urllib.parse
import xml.etree.ElementTree as ET

from .net import HttpClient, NetworkError


class FritzError(RuntimeError):
    pass


_ZERO_SID = "0" * 16


def _text(root, name):
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] == name:
            return (element.text or "").strip()
    return ""


def _parse_sid(xml):
    root = ET.fromstring(xml)
    return _text(root, "SID"), _text(root, "Challenge")


def _challenge_response(challenge, password):
    if challenge.startswith("2$"):
        parts = challenge.split("$")
        if len(parts) != 5:
            raise FritzError("unbekanntes FRITZ!Box-Challenge-Format")
        iterations1, salt1, iterations2, salt2 = parts[1:]
        first = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"),
            bytes.fromhex(salt1), int(iterations1)).hexdigest()
        second = hashlib.pbkdf2_hmac(
            "sha256", first.encode("ascii"),
            bytes.fromhex(salt2), int(iterations2)).hexdigest()
        return f"{second}${challenge}"
    digest = hashlib.md5(
        f"{challenge}-{password}".encode("utf-16le")).hexdigest()
    return f"{challenge}-{digest}"


class FritzBox:
    def __init__(self, host="fritz.box", password="", username="",
                 timeout=10.0):
        self.host = str(host)
        self.password = password
        self.username = username
        self.client = HttpClient(f"http://{self.host}", timeout=timeout)
        self.sid = None

    def login(self):
        try:
            response = self.client.request("/login_sid.lua?version=2")
        except NetworkError as error:
            raise FritzError(str(error)) from error
        sid, challenge = _parse_sid(response["body"].decode("utf-8", "replace"))
        if sid != _ZERO_SID and sid:
            self.sid = sid
            return sid
        answer = _challenge_response(challenge, self.password)
        query = urllib.parse.urlencode({"version": "2",
                                        "username": self.username,
                                        "response": answer})
        try:
            response = self.client.request(f"/login_sid.lua?{query}")
        except NetworkError as error:
            raise FritzError(str(error)) from error
        sid, _ = _parse_sid(response["body"].decode("utf-8", "replace"))
        if not sid or sid == _ZERO_SID:
            raise FritzError("FRITZ!Box-Login fehlgeschlagen")
        self.sid = sid
        return sid

    def _soap(self, service, action, arguments=None):
        if self.sid is None:
            self.login()
        values = "".join(f"<{key}>{value}</{key}>"
                         for key, value in (arguments or {}).items())
        body = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
            's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            f'<s:Body><u:{action} xmlns:u="urn:dslforum-org:service:'
            f'{service}:1">{values}</u:{action}></s:Body></s:Envelope>')
        url = (f"/upnp/control/{service}?sid="
               f"{urllib.parse.quote(self.sid)}")
        try:
            response = self.client.request(
                url, method="POST", data=body.encode("utf-8"), headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": f'"urn:dslforum-org:service:{service}:1#{action}"',
                })
        except NetworkError as error:
            raise FritzError(str(error)) from error
        if response["status"] != 200:
            raise FritzError(f"TR-064 HTTP {response['status']}")
        root = ET.fromstring(response["body"])
        result = {}
        for element in root.iter():
            name = element.tag.rsplit("}", 1)[-1]
            if name.startswith("New"):
                result[name[3:]] = (element.text or "").strip()
        return result

    def hosts(self):
        count = int(self._soap("hosts1", "GetHostNumberOfEntries")
                    .get("HostNumberOfEntries", 0))
        hosts = []
        for index in range(count):
            data = self._soap("hosts1", "GetGenericHostEntry",
                              {"NewIndex": index})
            if data:
                hosts.append(data)
        return hosts

    def wlan_info(self):
        return self._soap("wlanconfig1", "GetInfo")

    def wlan_enable(self, enabled):
        return self._soap("wlanconfig1", "SetEnable",
                          {"NewEnable": 1 if enabled else 0})
