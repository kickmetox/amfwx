"""Remote/IoT client tests with local mocks."""

from __future__ import annotations

import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import DeconzClient, FritzBox, TuyaCloud, WlanController
from amfwx.fritz import _challenge_response


class FritzHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/login_sid.lua"):
            if "response=" in self.path:
                body = "<SessionInfo><SID>sid123</SID></SessionInfo>"
            else:
                body = ("<SessionInfo><SID>0000000000000000</SID>"
                        "<Challenge>1234567890</Challenge></SessionInfo>")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        action = self.headers.get("SOAPAction", "")
        if "GetHostNumberOfEntries" in action:
            body = "<NewHostNumberOfEntries>1</NewHostNumberOfEntries>"
        elif "GetGenericHostEntry" in action:
            body = "<NewHostName>laptop</NewHostName>"
        elif "GetInfo" in action:
            body = "<NewEnable>1</NewEnable>"
        else:
            body = "<NewEnable>0</NewEnable>"
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode())


class DeconzHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"1":{"name":"Lamp","state":{"on":false}}}')

    def do_PUT(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'[{"success":{"/lights/1/state/on":true}}]')


class TuyaHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/v1.0/token"):
            body = ('{"success":true,"result":{"access_token":"tok",'
                    '"expire_time":3600}}')
        elif "/devices" in self.path:
            body = ('{"success":true,"result":[{"id":"d1",'
                    '"name":"Lamp"}]}')
        else:
            body = '{"success":true,"result":{}}'
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"success":true,"result":true}')


class RemoteTests(unittest.TestCase):
    def test_fritz(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), FritzHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            box = FritzBox(f"127.0.0.1:{server.server_port}", "secret")
            self.assertEqual(box.login(), "sid123")
            self.assertEqual(box.wlan_info()["Enable"], "1")
            self.assertEqual(box.hosts()[0]["HostName"], "laptop")
        finally:
            server.shutdown()
            server.server_close()

    def test_deconz(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), DeconzHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            client = DeconzClient("127.0.0.1", server.server_port, "key")
            self.assertIn("1", client.lights())
            self.assertTrue(client.on(1)[0]["success"])
        finally:
            server.shutdown()
            server.server_close()

    def test_tuya(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), TuyaHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            cloud = TuyaCloud("id", "secret",
                              base_url=f"http://127.0.0.1:{server.server_port}",
                              uid="u")
            self.assertEqual(cloud.devices()[0]["id"], "d1")
            self.assertTrue(cloud.switch("d1", True))
        finally:
            server.shutdown()
            server.server_close()

    def test_wlan(self):
        output = ("Name : WLAN\nDescription : Intel\n"
                  "State : connected\nSSID : Home\nSignal : 90%\n")
        calls = []

        def runner(command):
            calls.append(command)
            return output

        controller = WlanController(runner=runner)
        self.assertEqual(controller.current()["ssid"], "Home")
        controller.connect("Home")
        self.assertEqual(calls[-1][3], "name=Home")

    def test_fritz_v2_challenge(self):
        challenge = "2$1000$00112233445566778899aabbccddeeff$1000$ffeeddccbbaa99887766554433221100"
        response = _challenge_response(challenge, "secret")
        self.assertTrue(response.endswith("$" + challenge))
        self.assertGreater(len(response), len(challenge))


if __name__ == "__main__":
    unittest.main(verbosity=2)
