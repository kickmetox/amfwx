"""Zigbee2MQTT bridge client."""

from __future__ import annotations

import json
import time

from .mqtt import MqttClient, MqttError


class Zigbee2MqttError(RuntimeError):
    pass


class Zigbee2Mqtt:
    def __init__(self, host, port=1883, base_topic="zigbee2mqtt",
                 client_id="amfwx-z2m", username=None, password=None,
                 client_factory=None):
        self.host = host
        self.port = int(port)
        self.base_topic = str(base_topic).rstrip("/")
        self.client_id = client_id
        self.username = username
        self.password = password
        self.client_factory = client_factory or MqttClient

    def _client(self):
        return self.client_factory(
            self.host, self.port, client_id=self.client_id,
            username=self.username, password=self.password)

    def _read_json(self, topic, timeout=5.0):
        client = self._client()
        try:
            client.connect()
            client.subscribe(topic)
            deadline = time.monotonic() + float(timeout)
            while time.monotonic() < deadline:
                message = client.read_message(
                    timeout=max(0.1, deadline - time.monotonic()))
                if not message:
                    continue
                try:
                    return json.loads(message["payload"].decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    continue
        except MqttError as error:
            raise Zigbee2MqttError(str(error)) from error
        finally:
            client.close()
        raise Zigbee2MqttError(f"keine Antwort auf {topic}")

    def devices(self, timeout=5.0):
        return self._read_json(f"{self.base_topic}/bridge/devices", timeout)

    def state(self, name, timeout=5.0):
        return self._read_json(f"{self.base_topic}/{name}", timeout)

    def set(self, name, values):
        client = self._client()
        try:
            client.connect()
            client.publish(f"{self.base_topic}/{name}/set",
                           json.dumps(values))
        except MqttError as error:
            raise Zigbee2MqttError(str(error)) from error
        finally:
            client.close()
        return True

    def permit_join(self, seconds=60):
        client = self._client()
        try:
            client.connect()
            client.publish(f"{self.base_topic}/bridge/request/permit_join",
                           json.dumps({"value": True,
                                       "time": int(seconds)}))
        except MqttError as error:
            raise Zigbee2MqttError(str(error)) from error
        finally:
            client.close()
        return True
