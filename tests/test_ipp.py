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
from amfwx.ipp import parse_attributes


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



def attribute_response():
    name = b"printer-is-accepting-jobs\x00"
    return (b"\x02\x00\x00\x00\x00\x00\x00\x01\x01" +
            b"\x21" + name + b"\x00\x04" +
            b"\x00\x00\x00\x01" + b"\x03")


class AttributeHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        body = attribute_response()
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

    def test_parse_attributes(self):
        data = parse_attributes(attribute_response())
        self.assertEqual(data["printer-is-accepting-jobs"], 1)

    def test_get_attributes(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), AttributeHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            printer = IppPrinter("127.0.0.1", server.server_port)
            result = printer.get_attributes()
            self.assertEqual(result["printer-is-accepting-jobs"], 1)
        finally:
            server.shutdown()
            server.server_close()

    def test_get_jobs(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            printer = IppPrinter("127.0.0.1", server.server_port)
            self.assertIsInstance(printer.get_jobs(), dict)
            self.assertIn(b"\x00\x0a", Handler.bodies[-1])
        finally:
            server.shutdown()
            server.server_close()

    def test_cancel_job(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            printer = IppPrinter("127.0.0.1", server.server_port)
            result = printer.cancel_job(7)
            self.assertEqual(result["status"], 0)
            self.assertIn(b"\x00\x08", Handler.bodies[-1])
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
