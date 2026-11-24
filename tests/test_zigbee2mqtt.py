"""Zigbee2MQTT tests."""

from __future__ import annotations

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AppConfig, Zigbee2Mqtt


class FakeClient:
    instances = []

    def __init__(self, *args, **kwargs):
        self.subscribed = []
        self.published = []
        self.message = None
        FakeClient.instances.append(self)

    def connect(self):
        return self

    def subscribe(self, topic):
        self.subscribed.append(topic)
        return True

    def read_message(self, timeout=None):
        message, self.message = self.message, None
        return message

    def publish(self, topic, payload, retain=False):
        self.published.append((topic, payload))
        return True

    def close(self):
        pass


class ZigbeeTests(unittest.TestCase):
    def test_devices(self):
        client = FakeClient()
        client.message = {"topic": "zigbee2mqtt/bridge/devices",
                          "payload": json.dumps([{"friendly_name": "lamp"}]).encode()}
        zigbee = Zigbee2Mqtt("localhost", client_factory=lambda *a, **k: client)
        self.assertEqual(zigbee.devices(), [{"friendly_name": "lamp"}])
        self.assertIn("zigbee2mqtt/bridge/devices", client.subscribed)

    def test_set_and_permit(self):
        client = FakeClient()
        zigbee = Zigbee2Mqtt("localhost", client_factory=lambda *a, **k: client)
        zigbee.set("lamp", {"state": "ON"})
        zigbee.permit_join(30)
        self.assertEqual(client.published[0][0], "zigbee2mqtt/lamp/set")
        self.assertIn('"state": "ON"', client.published[0][1])
        self.assertEqual(client.published[1][0],
                         "zigbee2mqtt/bridge/request/permit_join")

    def test_cli(self):
        config = AppConfig.parse(["--zigbee-host", "localhost",
                                  "--zigbee-devices"])
        self.assertTrue(config.zigbee_devices)


if __name__ == "__main__":
    unittest.main(verbosity=2)
