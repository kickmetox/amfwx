"""MQTT subscribe/read tests."""

from __future__ import annotations

import os
import socketserver
import sys
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.mqtt import MqttClient


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        request = self.request
        request.recv(1024)  # CONNECT
        request.sendall(b"\x20\x02\x00\x00")
        request.recv(1024)  # SUBSCRIBE
        request.sendall(b"\x90\x03\x00\x01\x00")
        topic = b"jarolift/a1/state"
        payload = b"UP"
        body = len(topic).to_bytes(2, "big") + topic + payload
        request.sendall(b"\x30" + bytes([len(body)]) + body)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


class MqttSubscribeTests(unittest.TestCase):
    def test_subscribe_and_read(self):
        server = Server(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            client = MqttClient("127.0.0.1", server.server_address[1])
            client.connect()
            self.assertTrue(client.subscribe("jarolift/a1/state"))
            message = client.read_message(timeout=2)
            self.assertEqual(message["topic"], "jarolift/a1/state")
            self.assertEqual(message["payload"], b"UP")
            client.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
