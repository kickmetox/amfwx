"""Minimal MQTT 3.1.1 publisher (QoS 0) for local bridges."""

from __future__ import annotations

import socket


class MqttError(RuntimeError):
    pass


def encode_length(value):
    output = bytearray()
    while True:
        byte = value % 128
        value //= 128
        if value:
            byte |= 0x80
        output.append(byte)
        if not value:
            return bytes(output)


def encode_string(value):
    data = str(value).encode("utf-8")
    if len(data) > 65535:
        raise MqttError("MQTT-String zu lang")
    return len(data).to_bytes(2, "big") + data


class MqttClient:
    def __init__(self, host, port=1883, client_id="amfwx", username=None,
                 password=None, timeout=5.0):
        self.host = str(host)
        self.port = int(port)
        self.client_id = str(client_id)
        self.username = username
        self.password = password
        self.timeout = float(timeout)
        self.socket = None

    def connect(self):
        self.socket = socket.create_connection((self.host, self.port),
                                               timeout=self.timeout)
        flags = 0x02
        payload = encode_string(self.client_id)
        if self.username is not None:
            flags |= 0x80
            payload += encode_string(self.username)
        if self.password is not None:
            flags |= 0x40
            payload += encode_string(self.password)
        body = (encode_string("MQTT") + bytes([4, flags]) +
                (60).to_bytes(2, "big") + payload)
        packet = bytes([0x10]) + encode_length(len(body)) + body
        self.socket.sendall(packet)
        response = self.socket.recv(4)
        if len(response) != 4 or response[0] != 0x20 or response[3] != 0:
            raise MqttError("MQTT-CONNACK fehlgeschlagen")
        return self

    def publish(self, topic, payload, retain=False):
        if self.socket is None:
            self.connect()
        data = str(payload).encode("utf-8")
        body = encode_string(topic) + data
        header = 0x30 | (0x01 if retain else 0)
        packet = bytes([header]) + encode_length(len(body)) + body
        self.socket.sendall(packet)
        return True

    def close(self):
        if self.socket is not None:
            try:
                self.socket.sendall(b"\xe0\x00")
            except OSError:
                pass
            self.socket.close()
            self.socket = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, *_exc):
        self.close()
