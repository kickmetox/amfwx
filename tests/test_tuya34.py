"""Tuya 3.4 protocol tests with a fake device."""

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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from amfwx import AppConfig
from amfwx.tuya34 import (CMD_NEG_FINISH, CMD_NEG_RESP, CMD_NEG_START,
                          PREFIX, SUFFIX, TuyaLocal34, _aes, _hmac, _pad)


def frame(command, body, sequence=1):
    length = len(body) + 32 + 4
    header = struct.pack(">IIII", PREFIX, sequence, command, length)
    return header + body + _hmac(b"x", b"")[:0] + b"\x00" * 32 + struct.pack(">I", SUFFIX)


def read_frame(connection):
    header = b""
    while len(header) < 16:
        header += connection.recv(16 - len(header))
    _p, _s, command, length = struct.unpack(">IIII", header)
    body = b""
    while len(body) < length:
        body += connection.recv(length - len(body))
    body = body[:-4]
    return header, command, body


class Device:
    def __init__(self, key):
        self.key = key
        self.session = None
        self.device_nonce = os.urandom(16)

    def send(self, connection, command, plaintext, key, retcode=0):
        body = int(retcode).to_bytes(4, "big") + _aes(key, plaintext)
        length = len(body) + 32 + 4
        header = struct.pack(">IIII", PREFIX, 1, command, length)
        connection.sendall(header + body + _hmac(key, header + body) +
                           struct.pack(">I", SUFFIX))

    def run(self, connection):
        while True:
            try:
                header, command, body = read_frame(connection)
            except OSError:
                return
            encrypted, tag = body[:-32], body[-32:]
            if not hmac.compare_digest(tag, _hmac(self.key, header + encrypted)):
                return
            plain = _aes(self.key, encrypted, decrypt=True)
            if command == CMD_NEG_START:
                client_nonce = plain
                response = (self.device_nonce +
                            _hmac(self.key, client_nonce))
                self.send(connection, CMD_NEG_RESP, response, self.key)
                self.client_nonce = client_nonce
            elif command == CMD_NEG_FINISH:
                self.session = _aes(self.key, bytes(
                    a ^ b for a, b in zip(self.client_nonce,
                                          self.device_nonce)), pad=False)
                break
            else:
                break
        while True:
            try:
                header, command, body = read_frame(connection)
            except OSError:
                return
            encrypted, tag = body[:-32], body[-32:]
            if not hmac.compare_digest(tag, _hmac(self.session, header + encrypted)):
                return
            plain = _aes(self.session, encrypted, decrypt=True)
            if plain.startswith(b"3.4"):
                plain = plain[15:]
            payload = json.loads(plain.decode("utf-8"))
            answer = json.dumps({"dps": {"1": True},
                                 "echo": payload.get("dps")}).encode()
            self.send(connection, command, b"3.4" + b"\x00" * 12 + answer,
                      self.session)


@unittest.skipUnless(__import__('importlib').util.find_spec('cryptography'),
                     'cryptography fehlt')
class Tuya34Tests(unittest.TestCase):
    def test_handshake_and_status(self):
        key = "0123456789abcdef"
        real = hashlib.md5(key.encode()).digest()
        device = Device(real)
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
        client = TuyaLocal34("127.0.0.1", "dev", key, port=port)
        self.assertEqual(client.status()["dps"], {"1": True})
        self.assertIsNotNone(client.session_key)
        client.close()

    def test_cli(self):
        config = AppConfig.parse(["--tuya34-host", "h",
                                  "--tuya34-device", "d",
                                  "--tuya34-key", "k"])
        self.assertEqual(config.tuya34_device, "d")


if __name__ == "__main__":
    unittest.main(verbosity=2)
