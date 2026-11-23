"""HomePilot native client tests."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import HomePilot


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _json(self, payload, cookie=False):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", "session=ok; Path=/")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path.endswith("/password_salt"):
            self._json({"error_code": 0, "password_salt": "salt"})
        else:
            self._json({"error_code": 0}, cookie=True)

    def do_GET(self):
        if self.path == "/devices":
            if "session=ok" not in self.headers.get("Cookie", ""):
                self.send_response(401)
                self.end_headers()
                return
            self._json({"payload": {"devices": [{"did": 1,
                                                "name": "Rollladen"}]}})
        elif "devtype=Actuator" in self.path:
            self._json({"devices": [{"did": 1, "position": 50}]})
        elif "devtype=Sensor" in self.path:
            self._json({"meters": [{"did": 2, "temperature": 21}]})
        else:
            self._json({"transmitters": []})

    def do_PUT(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        self._json({"error_code": 0})


class HomePilotTests(unittest.TestCase):
    def test_devices_and_auth(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            pilot = HomePilot(f"127.0.0.1:{server.server_port}", "secret")
            self.assertTrue(pilot.login())
            self.assertEqual(pilot.devices()[0]["did"], 1)
            self.assertEqual(pilot.states()["1"]["position"], 50)
        finally:
            server.shutdown()
            server.server_close()

    def test_commands(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            pilot = HomePilot(f"127.0.0.1:{server.server_port}")
            self.assertEqual(pilot.open_cover(1)["error_code"], 0)
            self.assertEqual(pilot.set_position(1, 30)["error_code"], 0)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
