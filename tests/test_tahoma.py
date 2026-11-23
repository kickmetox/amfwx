"""TaHoma local API tests."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Tahoma

BASE = "/enduser-mobile-web/1/enduserAPI"


class Handler(BaseHTTPRequestHandler):
    auth = ""
    body = None

    def log_message(self, *args):
        pass

    def _send(self, payload):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        Handler.auth = self.headers.get("Authorization", "")
        if self.path == BASE + "/setup":
            self._send({"devices": [{"deviceURL": "io://1/2",
                                     "label": "Rollladen"}]})
        else:
            self._send([{"name": "core:ClosureState", "value": 40}])

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        if self.path.endswith("/events/register"):
            self._send({"id": "listener-1"})
        elif self.path.endswith("/fetch"):
            self._send([{"name": "DeviceStateChangedEvent"}])
        elif self.path.endswith("/unregister"):
            self._send([])
        else:
            Handler.body = json.loads(raw)
            self._send({"execId": "exec-1"})


class TahomaTests(unittest.TestCase):
    def test_setup_and_auth(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            tahoma = Tahoma("127.0.0.1", "token", server.server_port,
                            secure=False)
            self.assertEqual(tahoma.devices()[0]["label"], "Rollladen")
            self.assertEqual(Handler.auth, "Bearer token")
            self.assertEqual(tahoma.states("io://1/2")[0]["value"], 40)
        finally:
            server.shutdown()
            server.server_close()

    def test_execute(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            tahoma = Tahoma("127.0.0.1", "token", server.server_port,
                            secure=False)
            result = tahoma.set_position("io://1/2", 30)
            self.assertEqual(result["execId"], "exec-1")
            command = Handler.body["actions"][0]["commands"][0]
            self.assertEqual(command["name"], "setClosure")
            self.assertEqual(command["parameters"], [30])
        finally:
            server.shutdown()
            server.server_close()

    def test_events(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            tahoma = Tahoma("127.0.0.1", "token", server.server_port,
                            secure=False)
            self.assertEqual(tahoma.register_listener(), "listener-1")
            self.assertEqual(tahoma.fetch_events()[0]["name"],
                             "DeviceStateChangedEvent")
            tahoma.unregister_listener()
        finally:
            server.shutdown()
            server.server_close()

    def test_poll_events(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            tahoma = Tahoma("127.0.0.1", "token", server.server_port,
                            secure=False)
            stop = threading.Event()
            events = []

            def callback(event):
                events.append(event)
                stop.set()

            tahoma.poll_events(callback, interval=0.01, stop=stop)
            self.assertEqual(events[0]["name"], "DeviceStateChangedEvent")
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
