"""Becker CentralControl tests with a JSON-RPC mock."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import BeckerCentral
from amfwx.home_discovery import probe_becker


class Handler(BaseHTTPRequestHandler):
    calls = []

    def log_message(self, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8").rstrip("\0")
        request = json.loads(raw)
        Handler.calls.append(request)
        method = request["method"]
        if method == "deviced.deviced_get_item_list":
            if request["params"].get("item_type") == "remote":
                result = {"item_list": [{"id": 20,
                                         "remote_type": "sensor-wind"}]}
            else:
                result = {"item_list": [
                    {"id": 1, "name": "Salon", "device_type": "shutter",
                     "feedback": True},
                    {"id": 2, "name": "Terrasse", "device_type": "awning",
                     "feedback": True},
                    {"id": 9, "name": "Garage", "device_type": "door",
                     "feedback": True},
                ]}
        elif method == "deviced.group_get_state":
            result = {"state": {"value": 40, "moving_up": 0,
                                "moving_down": 0}}
        elif method == "deviced.item_get_state":
            result = {"state": {"value-wind": 2}}
        else:
            result = {}
        body = (json.dumps({"jsonrpc": "2.0", "id": request["id"],
                            "result": result}) + "\0").encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class BeckerTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.box = BeckerCentral("127.0.0.1", self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_groups(self):
        groups = self.box.groups()
        self.assertEqual([group["id"] for group in groups], [1, 2])
        self.assertEqual(self.box.remotes()[0]["id"], 20)

    def test_state(self):
        self.assertEqual(self.box.group_state(1)["value"], 40)
        self.assertEqual(self.box.item_state(20)["value-wind"], 2)

    def test_commands(self):
        self.box.open_cover(1)
        self.assertEqual(Handler.calls[-1]["params"],
                         {"group_id": 1, "command": "move", "value": -1})
        self.box.close_cover(2, "awning")
        self.assertEqual(Handler.calls[-1]["params"]["value"], -1)
        self.box.set_position(1, 30)
        self.assertEqual(Handler.calls[-1]["params"]["value"], 70)

    def test_probe(self):
        device = probe_becker("127.0.0.1", self.server.server_port)
        self.assertIsNotNone(device)
        self.assertEqual(device.kind, "becker")

    def test_sensors(self):
        sensors = self.box.sensors()
        self.assertEqual(sensors[0]["values"]["wind"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
