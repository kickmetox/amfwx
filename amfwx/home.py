"""Home-automation adapters.

Protocol-specific clients are implemented only where the local API is known.
Other systems use the generic HTTP/MQTT adapters with explicit paths/topics.
"""

from __future__ import annotations

import base64
import json

from .mqtt import MqttClient
from .net import HttpClient, NetworkError


class HomeError(RuntimeError):
    pass


class ShellyDevice:
    """Shelly Gen1/Gen2/Gen3 over local HTTP."""

    def __init__(self, host, port=80, timeout=8.0, secure=False):
        self.host = str(host)
        self.port = int(port)
        scheme = "https" if secure else "http"
        self.client = HttpClient(f"{scheme}://{self.host}:{self.port}",
                                 timeout=timeout)
        self._generation = None

    def _get(self, path):
        try:
            return self.client.json(path)
        except NetworkError as error:
            raise HomeError(str(error)) from error

    def _rpc(self, method, params=None):
        try:
            return self.client.json("/rpc/" + method, method="POST",
                                    json_data=params or {})
        except NetworkError as error:
            raise HomeError(str(error)) from error

    def info(self):
        return self._get("/shelly")

    def generation(self):
        if self._generation is None:
            data = self.info()
            self._generation = 2 if int(data.get("gen", 1)) >= 2 else 1
        return self._generation

    def status(self):
        return (self._rpc("Shelly.GetStatus")
                if self.generation() >= 2 else self._get("/status"))

    def open_cover(self, index=0):
        if self.generation() >= 2:
            return self._rpc("Cover.Open", {"id": int(index)})
        return self._get(f"/roller/{int(index)}?go=open")

    def close_cover(self, index=0):
        if self.generation() >= 2:
            return self._rpc("Cover.Close", {"id": int(index)})
        return self._get(f"/roller/{int(index)}?go=close")

    def stop_cover(self, index=0):
        if self.generation() >= 2:
            return self._rpc("Cover.Stop", {"id": int(index)})
        return self._get(f"/roller/{int(index)}?go=stop")

    def set_cover_position(self, position, index=0):
        position = max(0, min(100, int(position)))
        if self.generation() >= 2:
            return self._rpc("Cover.GoToPosition",
                             {"id": int(index), "pos": position})
        return self._get(f"/roller/{int(index)}?position={position}")

    def set_light(self, on=True, brightness=None, index=0):
        if self.generation() >= 2:
            params = {"id": int(index), "on": bool(on)}
            if brightness is not None:
                params["brightness"] = max(0, min(100, int(brightness)))
            return self._rpc("Light.Set", params)
        query = "on" if on else "off"
        path = f"/light/{int(index)}?turn={query}"
        if brightness is not None:
            path += f"&brightness={max(0, min(100, int(brightness)))}"
        return self._get(path)

    def set_thermostat(self, temperature, index=0):
        temperature = float(temperature)
        if self.generation() >= 2:
            return self._rpc("Thermostat.SetConfig", {
                "id": int(index),
                "config": {"target_C": temperature},
            })
        return self._get(f"/thermostat/{int(index)}?target_t={temperature}")


class FibaroHomeCenter:
    """Fibaro Home Center 2/3 REST API."""

    def __init__(self, host, port=80, username="admin", password="admin",
                 timeout=10.0, secure=False):
        self.host = str(host)
        self.port = int(port)
        scheme = "https" if secure else "http"
        token = base64.b64encode(
            f"{username}:{password}".encode("utf-8")).decode("ascii")
        self.client = HttpClient(f"{scheme}://{self.host}:{self.port}",
                                 timeout=timeout,
                                 headers={"Authorization": f"Basic {token}"})

    def devices(self):
        try:
            return self.client.json("/api/devices")
        except NetworkError as error:
            raise HomeError(str(error)) from error

    def call_action(self, device_id, action, arguments=None):
        query = {"deviceID": int(device_id), "name": action}
        query.update(arguments or {})
        path = "/api/callAction?" + "&".join(
            f"{key}={value}" for key, value in query.items())
        try:
            return self.client.json(path)
        except NetworkError as error:
            raise HomeError(str(error)) from error

    def open_cover(self, device_id):
        return self.call_action(device_id, "open")

    def close_cover(self, device_id):
        return self.call_action(device_id, "close")

    def set_temperature(self, device_id, temperature):
        return self.call_action(device_id, "setThermostatSetpoint",
                                {"value": float(temperature)})


class GenericHttpDevice:
    """Configurable HTTP adapter for systems without a dedicated client."""

    def __init__(self, base_url, status_path="/status",
                 command_path="/command", headers=None, timeout=8.0):
        self.client = HttpClient(base_url, timeout=timeout,
                                 headers=headers)
        self.status_path = status_path
        self.command_path = command_path

    def status(self):
        try:
            return self.client.json(self.status_path)
        except NetworkError as error:
            raise HomeError(str(error)) from error

    def command(self, action, **parameters):
        payload = {"action": action}
        payload.update(parameters)
        try:
            return self.client.json(self.command_path, method="POST",
                                    json_data=payload)
        except NetworkError as error:
            raise HomeError(str(error)) from error

    def on(self):
        return self.command("on")

    def off(self):
        return self.command("off")

    def open_cover(self):
        return self.command("open")

    def close_cover(self):
        return self.command("close")


class JaroliftBridge:
    """Jarolift 433 MHz bridge over MQTT (for example an ESP module)."""

    def __init__(self, host, port=1883, base_topic="jarolift",
                 username=None, password=None, client_id="amfwx-jarolift"):
        self.base_topic = str(base_topic).rstrip("/")
        self.mqtt = MqttClient(host, port, client_id=client_id,
                               username=username, password=password)

    def send(self, channel, command, retain=False):
        topic = f"{self.base_topic}/{channel}/set"
        payload = json.dumps({"command": str(command).upper()})
        self.mqtt.publish(topic, payload, retain=retain)
        return topic

    def up(self, channel):
        return self.send(channel, "UP")

    def down(self, channel):
        return self.send(channel, "DOWN")

    def stop(self, channel):
        return self.send(channel, "STOP")

    def close(self):
        self.mqtt.close()
