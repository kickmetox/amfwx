"""eSCL client tests with a local HTTP scanner mock."""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import EsclError, EsclScanner
from amfwx.escl import _settings_xml, parse_capabilities


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



class AuthHandler(Handler):
    auth = ""

    def do_GET(self):
        AuthHandler.auth = self.headers.get("Authorization", "")
        super().do_GET()



class FeederHandler(Handler):
    jobs = 0
    pages = 0
    served = set()

    def do_POST(self):
        if self.path != "/eSCL/ScanJobs":
            return super().do_POST()
        FeederHandler.jobs += 1
        self.send_response(201)
        self.send_header("Location", f"/eSCL/ScanJobs/{FeederHandler.jobs}")
        self.end_headers()

    def do_GET(self):
        if self.path == "/eSCL/ScannerStatus":
            state = "ScannerAdfLoaded" if FeederHandler.pages < 2 else "ScannerAdfEmpty"
            body = (f"<scan:ScannerStatus xmlns:scan='http://schemas.hp.com/imaging/escl/2011/05/03'>"
                    f"<scan:AdfState>{state}</scan:AdfState></scan:ScannerStatus>").encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.endswith("/NextDocument"):
            job = self.path.split("/")[-2]
            if job not in FeederHandler.served:
                FeederHandler.served.add(job)
                FeederHandler.pages += 1
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"\xff\xd8\xff\xd9")
            else:
                self.send_response(404)
                self.end_headers()
            return
        super().do_GET()



class EmptyAdfHandler(Handler):
    def do_POST(self):
        self.send_response(409)
        self.end_headers()

    def do_GET(self):
        if self.path == "/eSCL/ScannerStatus":
            body = (b"<scan:ScannerStatus xmlns:scan='http://schemas.hp.com/imaging/escl/2011/05/03'>"
                    b"<scan:AdfState>ScannerAdfEmpty</scan:AdfState></scan:ScannerStatus>")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
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

    def test_capabilities_parse(self):
        xml = ("<scan:ScannerCapabilities xmlns:scan='x'>"
               "<scan:MakeAndModel>Canon</scan:MakeAndModel>"
               "<scan:Adf/><scan:Duplex>true</scan:Duplex>"
               "<scan:XResolution>300</scan:XResolution>"
               "<scan:ColorMode>RGB24</scan:ColorMode>"
               "</scan:ScannerCapabilities>")
        caps = parse_capabilities(xml)
        self.assertEqual(caps.model, "Canon")
        self.assertTrue(caps.adf)
        self.assertTrue(caps.duplex)
        self.assertIn(300, caps.resolutions)
        self.assertIn("RGB24", caps.color_modes)

    def test_capabilities_platen(self):
        caps = parse_capabilities(
            "<scan:ScannerCapabilities xmlns:scan='x'>"
            "<scan:Platen/><scan:ColorModes>RGB24</scan:ColorModes>"
            "</scan:ScannerCapabilities>")
        self.assertTrue(caps.platen)
        self.assertIn("RGB24", caps.color_modes)

    def test_basic_auth(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), AuthHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            scanner = EsclScanner("127.0.0.1", server.server_port,
                                  username="user", password="secret")
            scanner.capabilities()
            self.assertTrue(AuthHandler.auth.startswith("Basic "))
        finally:
            server.shutdown()
            server.server_close()

    def test_secure_url(self):
        scanner = EsclScanner("scanner.local", secure=True)
        self.assertTrue(scanner.base_url.startswith("https://"))

    def test_tls_cert_missing(self):
        with self.assertRaises(FileNotFoundError):
            EsclScanner("example.invalid", secure=True,
                        certfile="missing-client.pem")

    def test_feeder_one_job_per_page(self):
        FeederHandler.jobs = 0
        FeederHandler.pages = 0
        FeederHandler.served = set()
        server = ThreadingHTTPServer(("127.0.0.1", 0), FeederHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            scanner = EsclScanner("127.0.0.1", server.server_port)
            with tempfile.TemporaryDirectory() as folder:
                pages = scanner.scan_pages(folder, prefix="page",
                                           source="Feeder", max_pages=5)
                self.assertEqual(len(pages), 2)
                self.assertEqual(FeederHandler.jobs, 2)
        finally:
            server.shutdown()
            server.server_close()

    def test_adf_empty_message(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), EmptyAdfHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            scanner = EsclScanner("127.0.0.1", server.server_port)
            with tempfile.TemporaryDirectory() as folder:
                with self.assertRaises(EsclError) as context:
                    scanner.scan_pages(folder, source="Feeder")
                self.assertIn("Einzug ist leer", str(context.exception))
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
