"""Tuya LAN protocol 3.4 client (session key + HMAC-SHA256)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import socket
import struct
import time

try:
    from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms,
                                                        modes)
except ImportError:  # optional dependency
    Cipher = None

PREFIX = 0x000055AA
SUFFIX = 0x0000AA55
CMD_CONTROL = 0x07
CMD_DP_QUERY = 0x0A
CMD_CONTROL_NEW = 0x0D
CMD_DP_QUERY_NEW = 0x10
CMD_NEG_START = 0x03
CMD_NEG_RESP = 0x04
CMD_NEG_FINISH = 0x05
VERSION_HEADER = b"3.4" + b"\x00" * 12


class Tuya34Error(RuntimeError):
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


def _aes(key, data, decrypt=False, pad=True):
    if pad and not decrypt:
        data = _pad(data)
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    worker = cipher.decryptor() if decrypt else cipher.encryptor()
    result = worker.update(data) + worker.finalize()
    return _unpad(result) if decrypt and pad else result


def _hmac(key, data):
    return hmac.new(key, data, hashlib.sha256).digest()


def _read_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise Tuya34Error("Tuya-Verbindung beendet")
        data += chunk
    return data


def _parse_frame(data):
    if len(data) < 24 or struct.unpack(">I", data[:4])[0] != PREFIX:
        raise Tuya34Error("ungueltiger Tuya-3.4-Rahmen")
    _prefix, sequence, command, length = struct.unpack(">IIII", data[:16])
    if len(data) < length + 16:
        raise Tuya34Error("kurzer Tuya-3.4-Rahmen")
    body = data[16:16 + length - 4]
    return command, body


class TuyaLocal34:
    def __init__(self, host, device_id, local_key, port=6668, timeout=4.0):
        if Cipher is None:
            raise Tuya34Error("cryptography fehlt: pip install cryptography")
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

    def _pack(self, command, plaintext, key, header=True, retcode=None):
        if header:
            plaintext = VERSION_HEADER + bytes(plaintext)
        encrypted = _aes(key, bytes(plaintext))
        body = (retcode + encrypted) if retcode is not None else encrypted
        length = len(body) + 32 + 4
        header = struct.pack(">IIII", PREFIX, self._next(), command, length)
        tag = _hmac(key, header + body)
        return header + body + tag + struct.pack(">I", SUFFIX)

    def _receive(self, key):
        header = _read_exact(self.socket, 16)
        _prefix, _sequence, command, length = struct.unpack(">IIII", header)
        if _prefix != PREFIX:
            raise Tuya34Error("falscher Prefix")
        rest = _read_exact(self.socket, length)
        if struct.unpack(">I", rest[-4:])[0] != SUFFIX:
            raise Tuya34Error("falscher Tuya-Footer")
        body = rest[:-4]
        if len(body) < 36:
            raise Tuya34Error("kurzer Tuya-Body")
        tag, encrypted = body[-32:], body[:-32]
        if not hmac.compare_digest(tag, _hmac(key, header + encrypted)):
            raise Tuya34Error("Tuya-HMAC ungueltig")
        retcode = encrypted[:4]
        return command, int.from_bytes(retcode, "big"), encrypted[4:]

    def connect(self):
        self.socket = socket.create_connection((self.host, self.port),
                                               timeout=self.timeout)
        self.client_nonce = os.urandom(16)
        self.socket.sendall(self._pack(CMD_NEG_START, self.client_nonce,
                                       self.real_key, header=False))
        command, retcode, encrypted = self._receive(self.real_key)
        if command != CMD_NEG_RESP or retcode != 0:
            raise Tuya34Error("Session-Start fehlgeschlagen")
        payload = _aes(self.real_key, encrypted, decrypt=True)
        if len(payload) < 48:
            raise Tuya34Error("kurze Session-Antwort")
        self.device_nonce = payload[:16]
        expected = _hmac(self.real_key, self.client_nonce)
        if not hmac.compare_digest(payload[16:48], expected):
            raise Tuya34Error("Session-HMAC ungueltig")
        finish = _hmac(self.real_key, self.device_nonce)
        self.socket.sendall(self._pack(CMD_NEG_FINISH, finish,
                                       self.real_key, header=False))
        xor = bytes(a ^ b for a, b in zip(self.client_nonce,
                                         self.device_nonce))
        self.session_key = _aes(self.real_key, xor, pad=False)
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
        self.socket.sendall(self._pack(command, payload, self.session_key))
        response, retcode, encrypted = self._receive(self.session_key)
        if retcode != 0:
            raise Tuya34Error(f"Tuya-Retcode {retcode}")
        plain = _aes(self.session_key, encrypted, decrypt=True)
        if plain.startswith(b"3.4"):
            plain = plain[15:]
        start = plain.find(b"{")
        end = plain.rfind(b"}")
        if start < 0 or end < start:
            raise Tuya34Error("keine JSON-Antwort")
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
