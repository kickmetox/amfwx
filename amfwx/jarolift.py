"""Jarolift control through an ESP32 Jarolift Controller (MQTT)."""

from __future__ import annotations

import json
import time

from .mqtt import MqttClient, MqttError


class JaroliftError(RuntimeError):
    pass


class JaroliftController:
    def __init__(self, host, port=1883, base_topic="ESP32-Jarolift-Controller",
                 username=None, password=None, tls=False, cafile=None,
                 insecure=False, client_factory=None):
        self.host = str(host)
        self.port = int(port)
        self.base_topic = str(base_topic).rstrip("/")
        self.username = username
        self.password = password
        self.tls = bool(tls)
        self.cafile = cafile
        self.insecure = bool(insecure)
        self.client_factory = client_factory or MqttClient

    def _client(self):
        return self.client_factory(
            self.host, self.port, client_id="amfwx-jarolift",
            username=self.username, password=self.password,
            tls=self.tls, cafile=self.cafile, insecure=self.insecure)

    def _publish(self, topic, payload):
        client = self._client()
        try:
            client.connect()
            client.publish(topic, str(payload))
        except MqttError as error:
            raise JaroliftError(str(error)) from error
        finally:
            client.close()
        return True

    def command(self, channel, action):
        channel = int(channel)
        if not 1 <= channel <= 16:
            raise JaroliftError("Kanal muss 1-16 sein")
        action = str(action).upper()
        if action not in ("UP", "OPEN", "DOWN", "CLOSE", "STOP", "SHADE"):
            raise JaroliftError(f"unbekannter Befehl: {action}")
        return self._publish(f"{self.base_topic}/cmd/shutter/{channel}", action)

    def group(self, group, action):
        group = int(group)
        if not 1 <= group <= 6:
            raise JaroliftError("Gruppe muss 1-6 sein")
        action = str(action).upper()
        return self._publish(f"{self.base_topic}/cmd/group/{group}", action)

    def position(self, channel, percent):
        channel = int(channel)
        percent = max(0, min(100, int(percent)))
        if not 1 <= channel <= 16:
            raise JaroliftError("Kanal muss 1-16 sein")
        return self._publish(f"{self.base_topic}/cmd/position/{channel}",
                             percent)

    def status(self, channel, timeout=3.0):
        client = self._client()
        topic = f"{self.base_topic}/status/shutter/{int(channel)}"
        try:
            client.connect()
            client.subscribe(topic)
            deadline = time.monotonic() + float(timeout)
            while time.monotonic() < deadline:
                message = client.read_message(
                    timeout=max(0.1, deadline - time.monotonic()))
                if not message:
                    continue
                payload = message["payload"].decode("utf-8", "replace")
                try:
                    return json.loads(payload)
                except ValueError:
                    return payload
        except MqttError as error:
            raise JaroliftError(str(error)) from error
        finally:
            client.close()
        raise JaroliftError(f"kein Status auf {topic}")

    def up(self, channel):
        return self.command(channel, "UP")

    def down(self, channel):
        return self.command(channel, "DOWN")

    def stop(self, channel):
        return self.command(channel, "STOP")

    def shade(self, channel):
        return self.command(channel, "SHADE")
