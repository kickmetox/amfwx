"""Printer subnet scan tests."""

from __future__ import annotations

import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, scan_network


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/eSCL/ScannerCapabilities":
            body = b"<scan:ScannerCapabilities/>"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


class PrinterScanTests(unittest.TestCase):
    def test_local_endpoint(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            endpoints = scan_network(
                "127.0.0.1/32", ports=(server.server_port,), timeout=1.0)
            self.assertEqual(len(endpoints), 1)
            self.assertTrue(endpoints[0].escl)
        finally:
            server.shutdown()
            server.server_close()

    def test_cli_parse(self):
        config = AppConfig.parse(["--scan-printers", "192.168.178.0/24"])
        self.assertEqual(config.scan_printers, "192.168.178.0/24")


if __name__ == "__main__":
    unittest.main(verbosity=2)
