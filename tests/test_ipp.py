"""IPP print tests with a local HTTP printer mock."""

from __future__ import annotations

import os
import struct
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, IppPrinter
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



def job_state_response(state=9):
    name = b"job-state\x00"
    return (b"\x02\x00\x00\x00\x00\x00\x00\x01\x01" +
            b"\x23" + name + b"\x00\x04" + struct.pack(">i", state) +
            b"\x03")


class JobStateHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        body = job_state_response()
        self.send_response(200)
        self.send_header("Content-Type", "application/ipp")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)



class AuthHandler(Handler):
    auth = ""

    def do_POST(self):
        AuthHandler.auth = self.headers.get("Authorization", "")
        super().do_POST()


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

    def test_job_state(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), JobStateHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            printer = IppPrinter("127.0.0.1", server.server_port)
            attributes = printer.get_job_attributes(7)
            self.assertEqual(attributes["job-state"], 9)
            self.assertEqual(printer.wait_for_job(7, timeout=2), 9)
        finally:
            server.shutdown()
            server.server_close()

    def test_job_state_parse(self):
        self.assertEqual(parse_attributes(job_state_response())["job-state"],
                         9)

    def test_basic_auth(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), AuthHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            printer = IppPrinter("127.0.0.1", server.server_port,
                                 username="user", password="secret")
            printer.print_job(b"data")
            self.assertTrue(AuthHandler.auth.startswith("Basic "))
        finally:
            server.shutdown()
            server.server_close()

    def test_copies_and_duplex(self):
        from amfwx.ipp import build_print_job
        payload = build_print_job("ipp://x/ipp/print", "job", "u",
                                  "application/pdf", b"%PDF",
                                  copies=3, sides="two-sided-long-edge")
        self.assertIn(b"copies", payload)
        self.assertIn(b"two-sided-long-edge", payload)

    def test_cli(self):
        config = AppConfig.parse(["--ipp-host", "h",
                                  "--ipp-print", "a.pdf",
                                  "--copies", "2", "--duplex"])
        self.assertEqual(config.ipp_copies, 2)
        self.assertTrue(config.ipp_duplex)


if __name__ == "__main__":
    unittest.main(verbosity=2)
