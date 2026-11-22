"""Optional OPC UA adapter.

The binary OPC UA stack is not reimplemented here. If the optional
``asyncua`` package is installed, this adapter provides a small sync API.
"""

from __future__ import annotations


class OpcUaError(RuntimeError):
    pass


class OpcUaClient:
    def __init__(self, url, timeout=5.0):
        self.url = str(url)
        self.timeout = float(timeout)
        self.client = None

    def _backend(self):
        try:
            from asyncua.sync import Client
        except ImportError as error:
            raise OpcUaError(
                "asyncua ist nicht installiert: pip install asyncua") from error
        return Client

    def connect(self):
        Client = self._backend()
        self.client = Client(self.url, timeout=self.timeout)
        self.client.connect()
        return self

    def read(self, node_id):
        if self.client is None:
            raise OpcUaError("nicht verbunden")
        return self.client.get_node(node_id).read_value()

    def write(self, node_id, value):
        if self.client is None:
            raise OpcUaError("nicht verbunden")
        self.client.get_node(node_id).write_value(value)
        return True

    def browse(self, node_id):
        if self.client is None:
            raise OpcUaError("nicht verbunden")
        return self.client.get_node(node_id).get_children()

    def disconnect(self):
        if self.client is not None:
            try:
                self.client.disconnect()
            finally:
                self.client = None
        return self

    def __enter__(self):
        return self.connect()

    def __exit__(self, *_exc):
        self.disconnect()
