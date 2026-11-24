"""Tuya LAN protocol 3.5 client (AES-GCM frames)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import socket
import struct
import time

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:  # optional dependency
    AESGCM = None

PREFIX = 0x00006699
SUFFIX = 0x00009966
CMD_CONTROL_NEW = 0x0D
CMD_DP_QUERY_NEW = 0x10
CMD_NEG_START = 0x03
CMD_NEG_RESP = 0x04
CMD_NEG_FINISH = 0x05
VERSION_HEADER = b"3.5" + b"\x00" * 12


class Tuya35Error(RuntimeError):
    pass


def _read_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise Tuya35Error("Tuya-Verbindung beendet")
        data += chunk
    return data


class TuyaLocal35:
    def __init__(self, host, device_id, local_key, port=6668, timeout=4.0):
        if AESGCM is None:
            raise Tuya35Error("cryptography fehlt: pip install cryptography")
        self.host = str(host)
        self.port = int(port)
        self.device_id = str(device_id)
        self.local_key = str(local_key)
        self.timeout = float(timeout)
        self.real_key = hashlib.md5(self.local_key.encode("utf-8")).digest()
        self.session_key = None
        self.sequence = 0
        self.socket = None
        self.client_nonce = b""
        self.device_nonce = b""

    def _next(self):
        self.sequence = (self.sequence + 1) & 0xFFFFFFFF
        return self.sequence

    def _frame(self, command, plaintext, key, retcode=None):
        payload = bytes(plaintext)
        if retcode is not None:
            payload = int(retcode).to_bytes(4, "big") + payload
        iv = os.urandom(12)
        length = 12 + len(payload) + 16
        header = (struct.pack(">I", PREFIX) + b"\x00\x00" +
                  struct.pack(">III", self._next(), command, length))
        encrypted = AESGCM(key).encrypt(iv, payload, header[4:])
        return header + iv + encrypted + struct.pack(">I", SUFFIX)

    def _receive(self, key):
        header = _read_exact(self.socket, 18)
        prefix = struct.unpack(">I", header[:4])[0]
        if prefix != PREFIX:
            raise Tuya35Error("falscher Prefix")
        _reserved, _sequence, command, length = struct.unpack(
            ">HIII", header[4:18])
        rest = _read_exact(self.socket, length + 4)
        if struct.unpack(">I", rest[-4:])[0] != SUFFIX:
            raise Tuya35Error("falscher Tuya-Footer")
        body = rest[:-4]
        iv, tag, ciphertext = body[:12], body[-16:], body[12:-16]
        try:
            plain = AESGCM(key).decrypt(iv, ciphertext + tag, header[4:])
        except Exception as error:
            raise Tuya35Error("GCM-Authentifizierung fehlgeschlagen") from error
        return command, plain

    @staticmethod
    def _strip(plain):
        if len(plain) >= 4 and plain[:4] == b"\x00\x00\x00\x00":
            plain = plain[4:]
        if plain.startswith(b"3.5"):
            plain = plain[15:]
        return plain

    def connect(self):
        self.socket = socket.create_connection((self.host, self.port),
                                               timeout=self.timeout)
        self.client_nonce = os.urandom(16)
        self.socket.sendall(self._frame(CMD_NEG_START, self.client_nonce,
                                        self.real_key))
        command, payload = self._receive(self.real_key)
        payload = self._strip(payload)
        if command != CMD_NEG_RESP or len(payload) < 48:
            raise Tuya35Error("Session-Start fehlgeschlagen")
        self.device_nonce = payload[:16]
        expected = hmac.new(self.real_key, self.client_nonce,
                            hashlib.sha256).digest()
        if not hmac.compare_digest(payload[16:48], expected):
            raise Tuya35Error("Session-HMAC ungueltig")
        finish = hmac.new(self.real_key, self.device_nonce,
                          hashlib.sha256).digest()
        self.socket.sendall(self._frame(CMD_NEG_FINISH, finish,
                                        self.real_key))
        xor = bytes(a ^ b for a, b in zip(self.client_nonce,
                                         self.device_nonce))
        self.session_key = AESGCM(self.real_key).encrypt(
            self.client_nonce[:12], xor, b"")[:16]
        return self

    def close(self):
        if self.socket is not None:
            try:
                self.socket.close()
            finally:
                self.socket = None

    def _transact(self, command, payload):
        if self.session_key is None:
            self.connect()
        self.socket.sendall(self._frame(
            command, VERSION_HEADER + payload, self.session_key))
        response, plain = self._receive(self.session_key)
        if len(plain) >= 4 and plain[:4] != b"\x00\x00\x00\x00":
            raise Tuya35Error(f"Tuya-Retcode {int.from_bytes(plain[:4], 'big')}")
        plain = self._strip(plain)
        start = plain.find(b"{")
        end = plain.rfind(b"}")
        if start < 0 or end < start:
            raise Tuya35Error("keine JSON-Antwort")
        return json.loads(plain[start:end + 1].decode("utf-8", "replace"))

    def status(self):
        payload = json.dumps({"devId": self.device_id,
                              "uid": self.device_id,
                              "t": int(time.time())}).encode("utf-8")
        return self._transact(CMD_DP_QUERY_NEW, payload)

    def set_dps(self, dps):
        payload = json.dumps({"devId": self.device_id,
                              "uid": self.device_id,
                              "t": int(time.time()),
                              "dps": {str(k): v for k, v in dps.items()}}
                             ).encode("utf-8")
        return self._transact(CMD_CONTROL_NEW, payload)

    def switch(self, enabled, dp=1):
        return self.set_dps({int(dp): bool(enabled)})

    def __enter__(self):
        return self.connect()

    def __exit__(self, *_exc):
        self.close()
