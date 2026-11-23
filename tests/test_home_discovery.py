"""Home discovery tests."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import discover_home, probe_http
from amfwx.home_discovery import parse_ssdp


class ShellyHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        body = json.dumps({"type": "SHSW-25", "mac": "AABBCC"}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class FibaroHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path != "/api/devices":
            self.send_response(404)
            self.end_headers()
            return
        body = b'[{"id": 1, "name": "Light"}]'
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class DiscoveryTests(unittest.TestCase):
    def test_probe_shelly(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), ShellyHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            device = probe_http("127.0.0.1", server.server_port)
            self.assertIsNotNone(device)
            self.assertEqual(device.kind, "shelly")
        finally:
            server.shutdown()
            server.server_close()

    def test_probe_fibaro(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), FibaroHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            device = probe_http("127.0.0.1", server.server_port)
            self.assertIsNotNone(device)
            self.assertEqual(device.kind, "fibaro")
        finally:
            server.shutdown()
            server.server_close()

    def test_ssdp(self):
        parsed = parse_ssdp(
            b"HTTP/1.1 200 OK\r\nLOCATION: http://192.168.1.2/x\r\n"
            b"ST: upnp:rootdevice\r\nSERVER: Linux\r\n")
        self.assertEqual(parsed["host"], "192.168.1.2")

    def test_discover_home(self):
        self.assertIsInstance(discover_home(timeout=0), list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
