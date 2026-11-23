"""Tuya LAN 3.3 tests with a local TCP device mock."""

from __future__ import annotations

import json
import os
import socket
import socketserver
import struct
import sys
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.tuya_local import (PREFIX, SUFFIX, TuyaLocal, TuyaLocalError)


def available():
    from amfwx import tuya_local
    return tuya_local.Cipher is not None


class Handler(socketserver.BaseRequestHandler):
    payloads = []
    client = None

    def handle(self):
        header = self.request.recv(16)
        if len(header) < 16:
            return
        _prefix, seq, command, length = struct.unpack(">IIII", header)
        body = b""
        while len(body) < length:
            chunk = self.request.recv(length - len(body))
            if not chunk:
                break
            body += chunk
        encrypted = body[:max(0, length - 8)]
        if encrypted:
            Handler.payloads.append(Handler.client.decrypt(encrypted))
        response = json.dumps({"devId": "dev", "dps": {"1": True}}).encode()
        encrypted = Handler.client.encrypt(response)
        frame = (struct.pack(">IIII", PREFIX, seq, command, len(encrypted) + 8) +
                 encrypted + b"\x00\x00\x00\x00" + struct.pack(">I", SUFFIX))
        self.request.sendall(frame)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


@unittest.skipUnless(available(), "cryptography fehlt")
class TuyaLocalTests(unittest.TestCase):
    def setUp(self):
        Handler.payloads = []
        Handler.client = TuyaLocal("127.0.0.1", "dev", "0123456789abcdef")
        self.server = Server(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.device = TuyaLocal("127.0.0.1", "dev", "0123456789abcdef",
                                port=self.server.server_address[1])

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_status(self):
        self.assertTrue(self.device.status()["dps"]["1"])

    def test_switch(self):
        self.device.off(1)
        payload = json.loads(Handler.payloads[-1].decode())
        self.assertEqual(payload["dps"], {"1": False})


if __name__ == "__main__":
    unittest.main(verbosity=2)
