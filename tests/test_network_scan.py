"""Network scanner/printer discovery tests."""

from __future__ import annotations

import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import NetworkDevice, discover_network_devices, probe_escl


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/eSCL/ScannerCapabilities":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<scan/>")
        else:
            self.send_response(404)
            self.end_headers()


class NetworkScanTests(unittest.TestCase):
    def test_kind(self):
        self.assertEqual(NetworkDevice("a", "_uscan._tcp").kind, "scanner")
        self.assertEqual(NetworkDevice("b", "_ipp._tcp").kind, "printer")

    def test_probe_escl(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            self.assertTrue(probe_escl("127.0.0.1", server.server_port))
        finally:
            server.shutdown()
            server.server_close()

    def test_discovery_returns_list(self):
        self.assertIsInstance(discover_network_devices(timeout=0.1), list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
