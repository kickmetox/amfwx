"""GoPro HTTP tests."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import GoProCamera


class Handler(BaseHTTPRequestHandler):
    paths = []

    def log_message(self, *args):
        pass

    def do_GET(self):
        Handler.paths.append(self.path)
        body = json.dumps({"status": 0}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class GoProTests(unittest.TestCase):
    def test_status_and_photo(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            camera = GoProCamera("127.0.0.1", server.server_port)
            self.assertEqual(camera.status()["status"], 0)
            camera.take_photo()
            self.assertIn("/gp/gpControl/command/shutter?p=1", Handler.paths)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
