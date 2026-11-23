"""End-to-end CLI device control against a Shelly mock."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import HomeRegistry


class Handler(BaseHTTPRequestHandler):
    paths = []

    def log_message(self, *args):
        pass

    def do_GET(self):
        Handler.paths.append(self.path)
        if self.path == "/shelly":
            payload = {"type": "SHSW-25"}
        else:
            payload = {"ok": True}
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Device:
    kind = "shelly"
    name = "Lamp"
    host = "127.0.0.1"
    port = 80


class CliDeviceTests(unittest.TestCase):
    def test_open(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            Device.port = server.server_port
            with tempfile.TemporaryDirectory() as folder:
                path = os.path.join(folder, "devices.json")
                registry = HomeRegistry(path)
                registry.add(Device())
                registry.save()
                result = subprocess.run(
                    [sys.executable, "-m", "amfwx", "--device", "Lamp",
                     "--action", "open", "--registry", path],
                    capture_output=True, text=True,
                    cwd=os.path.dirname(os.path.dirname(
                        os.path.abspath(__file__))))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("ok", result.stdout)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
