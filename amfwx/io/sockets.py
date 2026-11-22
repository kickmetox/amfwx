"""TCP/UDP socket helpers for device and network protocols."""

from __future__ import annotations

import socket


class SocketError(RuntimeError):
    pass


class TcpClient:
    def __init__(self, host, port, timeout=5.0):
        self.host = str(host)
        self.port = int(port)
        self.timeout = float(timeout)
        self.socket = None

    def connect(self):
        self.socket = socket.create_connection((self.host, self.port),
                                               timeout=self.timeout)
        return self

    def send(self, data):
        if self.socket is None:
            raise SocketError("nicht verbunden")
        self.socket.sendall(bytes(data))
        return self

    def recv(self, size=4096):
        if self.socket is None:
            raise SocketError("nicht verbunden")
        return self.socket.recv(int(size))

    def recv_until(self, marker=b"\n", maximum=1024 * 1024):
        data = bytearray()
        while marker not in data:
            chunk = self.recv(4096)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > maximum:
                raise SocketError("Antwort zu gross")
        return bytes(data)

    def close(self):
        if self.socket is not None:
            try:
                self.socket.close()
            finally:
                self.socket = None
        return self

    def __enter__(self):
        return self.connect()

    def __exit__(self, *_exc):
        self.close()


class UdpSocket:
    def __init__(self, host="0.0.0.0", port=0, timeout=5.0,
                 broadcast=False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(float(timeout))
        self.socket.bind((str(host), int(port)))
        if broadcast:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send(self, data, host, port):
        self.socket.sendto(bytes(data), (str(host), int(port)))
        return self

    def recv(self, size=4096):
        data, address = self.socket.recvfrom(int(size))
        return data, address

    def close(self):
        self.socket.close()
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
