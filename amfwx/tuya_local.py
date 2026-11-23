"""Tuya LAN protocol 3.3 client (AES-128-ECB)."""

from __future__ import annotations

import hashlib
import json
import socket
import struct
import time

PREFIX = 0x000055AA
SUFFIX = 0x0000AA55
CMD_CONTROL = 0x07
CMD_DP_QUERY = 0x0A
CMD_DP_QUERY_NEW = 0x10

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ImportError:  # optional dependency
    Cipher = None


class TuyaLocalError(RuntimeError):
    pass


def _pad(data):
    length = 16 - (len(data) % 16)
    return data + bytes([length]) * length


def _unpad(data):
    if not data:
        return data
    length = data[-1]
    if 1 <= length <= 16:
        return data[:-length]
    return data


class TuyaLocal:
    def __init__(self, host, device_id, local_key, port=6668, timeout=3.0):
        if Cipher is None:
            raise TuyaLocalError("cryptography fehlt: pip install cryptography")
        self.host = str(host)
        self.port = int(port)
        self.device_id = str(device_id)
        self.local_key = str(local_key)
        self.timeout = float(timeout)
        self.key = hashlib.md5(self.local_key.encode("utf-8")).digest()
        self.sequence = 0

    def _crypt(self, data, encrypt=True):
        cipher = Cipher(algorithms.AES(self.key), modes.ECB())
        worker = cipher.encryptor() if encrypt else cipher.decryptor()
        return worker.update(data) + worker.finalize()

    def encrypt(self, data):
        return self._crypt(_pad(bytes(data)), True)

    def decrypt(self, data):
        return _unpad(self._crypt(bytes(data), False))

    def build_frame(self, command, payload):
        self.sequence = (self.sequence + 1) & 0xFFFFFFFF
        length = len(payload) + 8
        return (struct.pack(">IIII", PREFIX, self.sequence, command, length) +
                payload + b"\x00\x00\x00\x00" + struct.pack(">I", SUFFIX))

    @staticmethod
    def parse_frame(data):
        if len(data) < 24 or struct.unpack(">I", data[:4])[0] != PREFIX:
            raise TuyaLocalError("ungueltiger Tuya-Rahmen")
        _prefix, _seq, command, length = struct.unpack(">IIII", data[:16])
        payload = data[16:16 + max(0, length - 8)]
        return command, payload

    def _request(self, command, payload):
        frame = self.build_frame(command, self.encrypt(payload))
        sock = socket.create_connection((self.host, self.port),
                                        timeout=self.timeout)
        try:
            sock.sendall(frame)
            header = sock.recv(16)
            if len(header) < 16:
                raise TuyaLocalError("kurze Tuya-Antwort")
            _prefix, _seq, response_command, length = struct.unpack(">IIII", header)
            body = b""
            while len(body) < length:
                chunk = sock.recv(length - len(body))
                if not chunk:
                    break
                body += chunk
        finally:
            sock.close()
        encrypted = body[:max(0, length - 8)]
        if not encrypted:
            return response_command, b""
        return response_command, self.decrypt(encrypted)

    @staticmethod
    def _json(payload):
        start = payload.find(b"{")
        end = payload.rfind(b"}")
        if start < 0 or end < start:
            raise TuyaLocalError("keine JSON-Antwort")
        try:
            return json.loads(payload[start:end + 1].decode("utf-8", "replace"))
        except ValueError as error:
            raise TuyaLocalError("ungueltige Tuya-JSON-Antwort") from error

    def status(self):
        timestamp = int(time.time())
        payload = json.dumps({"gwId": self.device_id,
                              "devId": self.device_id,
                              "uid": self.device_id,
                              "t": timestamp}).encode("utf-8")
        _command, response = self._request(CMD_DP_QUERY, payload)
        return self._json(response)

    def set_dps(self, dps):
        timestamp = int(time.time())
        first = json.dumps({"devId": self.device_id,
                            "uid": self.device_id,
                            "t": timestamp,
                            "dpId": [int(key) for key in dps]}).encode("utf-8")
        self._request(CMD_CONTROL, first)
        second = json.dumps({"devId": self.device_id,
                             "uid": self.device_id,
                             "t": timestamp,
                             "dps": {str(key): value
                                     for key, value in dps.items()}}
                            ).encode("utf-8")
        _command, response = self._request(CMD_CONTROL, second)
        return self._json(response)

    def switch(self, enabled, dp=1):
        return self.set_dps({int(dp): bool(enabled)})

    def on(self, dp=1):
        return self.switch(True, dp)

    def off(self, dp=1):
        return self.switch(False, dp)
