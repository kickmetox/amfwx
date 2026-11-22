"""In-memory serial loopback for tests without hardware."""

from __future__ import annotations


class LoopbackSerial:
    def __init__(self, echo=False):
        self.inbox = bytearray()
        self.outbox = bytearray()
        self.echo = bool(echo)
        self.peer = None

    def write(self, data):
        payload = bytes(data)
        self.outbox.extend(payload)
        target = self.peer if self.peer is not None else self
        target.inbox.extend(payload)
        return len(payload)

    def read(self, size=1):
        size = max(0, int(size))
        data = bytes(self.inbox[:size])
        del self.inbox[:size]
        return data

    def flush(self):
        self.inbox.clear()
        self.outbox.clear()
        return self

    def close(self):
        return self

    @classmethod
    def pair(cls):
        first = cls(echo=False)
        second = cls(echo=False)
        first.peer = second
        second.peer = first
        return first, second
