"""Tuya 3.5 GCM tests with a fake device."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import socket
import struct
import sys
import threading
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from amfwx import AppConfig
from amfwx.tuya35 import (CMD_NEG_FINISH, CMD_NEG_RESP, CMD_NEG_START,
                          PREFIX, SUFFIX, TuyaLocal35)


def pack(command, plaintext, key, sequence=1):
    iv = os.urandom(12)
    length = 12 + len(plaintext) + 16
    header = (struct.pack(">I", PREFIX) + b"\x00\x00" +
              struct.pack(">III", sequence, command, length))
    encrypted = AESGCM(key).encrypt(iv, plaintext, header[4:])
    return header + iv + encrypted + struct.pack(">I", SUFFIX)


def read_frame(connection):
    header = b""
    while len(header) < 18:
        header += connection.recv(18 - len(header))
    _reserved, _seq, command, length = struct.unpack(">HIII", header[4:18])
    rest = b""
    while len(rest) < length + 4:
        rest += connection.recv(length + 4 - len(rest))
    body = rest[:-4]
    return header, command, body


class Device:
    def __init__(self, key):
        self.key = key
        self.session = None
        self.device_nonce = os.urandom(16)

    @staticmethod
    def unpack(body, key, aad):
        return AESGCM(key).decrypt(body[:12], body[12:], aad)

    def run(self, connection):
        while True:
            header, command, body = read_frame(connection)
            plain = self.unpack(body, self.key, header[4:])
            if command == CMD_NEG_START:
                self.client_nonce = plain
                response = self.device_nonce + hmac.new(
                    self.key, self.client_nonce, hashlib.sha256).digest()
                connection.sendall(pack(CMD_NEG_RESP, response, self.key))
            elif command == CMD_NEG_FINISH:
                self.session = AESGCM(self.key).encrypt(
                    self.client_nonce[:12], bytes(
                        a ^ b for a, b in zip(self.client_nonce,
                                              self.device_nonce)), b"")[:16]
                break
        while True:
            header, command, body = read_frame(connection)
            plain = self.unpack(body, self.session, header[4:])
            if plain[:4] == b"\x00" * 4:
                plain = plain[4:]
            if plain.startswith(b"3.5"):
                plain = plain[15:]
            payload = json.loads(plain.decode("utf-8"))
            answer = b"3.5" + b"\x00" * 12 + json.dumps(
                {"dps": {"1": True}, "echo": payload.get("dps")}).encode()
            connection.sendall(pack(command, b"\x00" * 4 + answer,
                                    self.session))


class Tuya35Tests(unittest.TestCase):
    def test_handshake_and_status(self):
        key = "0123456789abcdef"
        device = Device(hashlib.md5(key.encode()).digest())
        server = socket.socket()
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def serve():
            connection, _ = server.accept()
            try:
                device.run(connection)
            except Exception:
                import traceback; traceback.print_exc()
            finally:
                connection.close()
                server.close()

        threading.Thread(target=serve, daemon=True).start()
        client = TuyaLocal35("127.0.0.1", "dev", key, port=port)
        self.assertEqual(client.status()["dps"], {"1": True})
        self.assertIsNotNone(client.session_key)
        client.close()

    def test_cli(self):
        config = AppConfig.parse(["--tuya35-host", "h",
                                  "--tuya35-device", "d",
                                  "--tuya35-key", "k"])
        self.assertEqual(config.tuya35_device, "d")


if __name__ == "__main__":
    unittest.main(verbosity=2)
