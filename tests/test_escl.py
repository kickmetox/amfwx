"""eSCL client tests with a local HTTP scanner mock."""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import EsclScanner
from amfwx.escl import _settings_xml


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/eSCL/ScannerCapabilities":
            body = b"<scan:ScannerCapabilities/>"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/eSCL/ScanJobs/1/NextDocument":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"\xff\xd8\xff\xd9")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/eSCL/ScanJobs":
            self.send_response(201)
            self.send_header("Location", "/eSCL/ScanJobs/1")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


class PageHandler(Handler):
    def do_GET(self):
        if self.path == "/eSCL/ScanJobs/1/NextDocument":
            self.server.pages = getattr(self.server, "pages", 0) + 1
            if self.server.pages <= 2:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"\xff\xd8\xff\xd9")
            else:
                self.send_response(404)
                self.end_headers()
        else:
            super().do_GET()


class EsclTests(unittest.TestCase):
    def test_capabilities_and_scan(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            scanner = EsclScanner("127.0.0.1", server.server_port)
            self.assertIn("ScannerCapabilities", scanner.capabilities())
            with tempfile.TemporaryDirectory() as folder:
                path = os.path.join(folder, "scan.jpg")
                self.assertEqual(scanner.scan(path), path)
                self.assertTrue(os.path.getsize(path) > 0)
        finally:
            server.shutdown()
            server.server_close()

    def test_settings(self):
        xml = _settings_xml(600, "RGB24", "image/png")
        self.assertIn(b"<scan:XResolution>600</scan:XResolution>", xml)
        self.assertIn(b"image/png", xml)

    def test_multipage(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), PageHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            scanner = EsclScanner("127.0.0.1", server.server_port)
            with tempfile.TemporaryDirectory() as folder:
                pages = scanner.scan_pages(folder, prefix="page")
                self.assertEqual(len(pages), 2)
        finally:
            server.shutdown()
            server.server_close()

    def test_duplex_region(self):
        xml = _settings_xml(300, "RGB24", "image/jpeg", True,
                            (10, 20, 100, 200))
        self.assertIn(b"<scan:Duplex>true</scan:Duplex>", xml)
        self.assertIn(b"<pwg:XOffset>10</pwg:XOffset>", xml)
        self.assertIn(b"<pwg:Width>100</pwg:Width>", xml)


if __name__ == "__main__":
    unittest.main(verbosity=2)
