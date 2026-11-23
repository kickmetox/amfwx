"""HTTP Digest authentication tests."""

from __future__ import annotations

import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.net import HttpClient


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        auth = self.headers.get("Authorization", "")
        if not auth:
            self.send_response(401)
            self.send_header(
                "WWW-Authenticate",
                'Digest realm="test", nonce="abc", qop="auth"')
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


class DigestTests(unittest.TestCase):
    def test_header(self):
        header = HttpClient._digest_header(
            'Digest realm="test", nonce="abc", qop="auth"',
            "GET", "/x", "user", "pass")
        self.assertIn('username="user"', header)
        self.assertIn('realm="test"', header)
        self.assertIn("response=", header)

    def test_retry(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = HttpClient(f"http://127.0.0.1:{server.server_port}",
                                username="user", password="pass")
            response = client.request("/x")
            self.assertEqual(response["status"], 200)
            self.assertEqual(response["body"], b"ok")
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
