"""Home automation adapter tests."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.home import (FibaroHomeCenter, GenericHttpDevice, JaroliftBridge,
                        ShellyDevice)
from amfwx.mqtt import encode_length


class ShellyHandler(BaseHTTPRequestHandler):
    gen = 1
    posts = []

    def log_message(self, *args):
        pass

    def _send(self, payload):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/shelly":
            self._send({"type": "SHSW-25", "gen": self.gen})
        elif self.path.startswith("/roller/0"):
            self._send({"ok": True})
        else:
            self._send({"ok": True})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        ShellyHandler.posts.append((self.path, self.rfile.read(length)))
        self._send({"ok": True})


class FibaroHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/api/scenes":
            payload = [{"id": 7, "name": "Abend"}]
        elif self.path == "/api/devices":
            payload = [{"id": 1, "name": "Rollladen"}]
        else:
            payload = [{"id": 1, "result": True}]
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        body = b'[{"id": 7, "result": true}]'
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class HomeTests(unittest.TestCase):
    def test_shelly_gen1(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), ShellyHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            ShellyHandler.gen = 1
            device = ShellyDevice("127.0.0.1", server.server_port)
            self.assertEqual(device.generation(), 1)
            self.assertTrue(device.open_cover()["ok"])
        finally:
            server.shutdown()
            server.server_close()

    def test_shelly_gen2(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), ShellyHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            ShellyHandler.gen = 2
            device = ShellyDevice("127.0.0.1", server.server_port)
            self.assertEqual(device.generation(), 2)
            device.set_cover_position(40)
            self.assertTrue(ShellyHandler.posts[-1][0].endswith(
                "/rpc/Cover.GoToPosition"))
        finally:
            server.shutdown()
            server.server_close()

    def test_fibaro(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), FibaroHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            center = FibaroHomeCenter("127.0.0.1", server.server_port)
            self.assertEqual(center.devices()[0]["id"], 1)
            self.assertTrue(center.open_cover(1)[0]["result"])
        finally:
            server.shutdown()
            server.server_close()

    def test_jarolift(self):
        class Recorder:
            def __init__(self):
                self.sent = []

            def publish(self, topic, payload, retain=False):
                self.sent.append((topic, payload, retain))

        bridge = JaroliftBridge("127.0.0.1")
        bridge.mqtt = Recorder()
        topic = bridge.up("a1b2")
        self.assertEqual(topic, "jarolift/a1b2/set")
        self.assertIn('"UP"', bridge.mqtt.sent[0][1])

    def test_mqtt_length(self):
        self.assertEqual(encode_length(0), b"\x00")
        self.assertEqual(encode_length(127), b"\x7f")
        self.assertEqual(encode_length(128), b"\x80\x01")

    def test_fibaro_scenes(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), FibaroHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            center = FibaroHomeCenter("127.0.0.1", server.server_port)
            self.assertEqual(center.scenes()[0]["name"], "Abend")
            self.assertTrue(center.execute_scene(7)[0]["result"])
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
