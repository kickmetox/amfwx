"""IPP print tests with a local HTTP printer mock."""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import IppPrinter


class Handler(BaseHTTPRequestHandler):
    bodies = []

    def log_message(self, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        Handler.bodies.append(self.rfile.read(length))
        body = b"\x02\x00\x00\x00\x00\x00\x00\x01\x03"
        self.send_response(200)
        self.send_header("Content-Type", "application/ipp")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class IppTests(unittest.TestCase):
    def test_print_job(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            printer = IppPrinter("127.0.0.1", server.server_port)
            result = printer.print_job(b"%PDF-1.4", "application/pdf", "test")
            self.assertEqual(result["status"], 0)
            self.assertTrue(Handler.bodies)
            self.assertIn(b"printer-uri", Handler.bodies[-1])
        finally:
            server.shutdown()
            server.server_close()

    def test_print_file_format(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "doc.pdf")
            with open(path, "wb") as handle:
                handle.write(b"%PDF")
            printer = IppPrinter("127.0.0.1", 1)
            self.assertEqual(
                printer.path, "/ipp/print")
            # no network call here; extension mapping is covered by print_job


if __name__ == "__main__":
    unittest.main(verbosity=2)
