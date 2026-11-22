"""Minimal Modbus TCP client."""

from __future__ import annotations

import socket
import struct


class ModbusError(RuntimeError):
    pass


class ModbusTCP:
    def __init__(self, host, port=502, unit=1, timeout=3.0):
        self.host = str(host)
        self.port = int(port)
        self.unit = int(unit)
        self.timeout = float(timeout)
        self._transaction = 0

    def _request(self, pdu):
        self._transaction = (self._transaction + 1) & 0xFFFF
        header = struct.pack(">HHHB", self._transaction, 0,
                             len(pdu) + 1, self.unit)
        with socket.create_connection((self.host, self.port),
                                      timeout=self.timeout) as sock:
            sock.sendall(header + pdu)
            reply = self._recv_exact(sock, 7)
            _tid, _pid, length, _unit = struct.unpack(">HHHB", reply)
            body = self._recv_exact(sock, max(0, length - 1))
        if not body:
            raise ModbusError("leere Antwort")
        if body[0] & 0x80:
            raise ModbusError(f"Modbus-Exception {body[1] if len(body) > 1 else '?'}")
        return body

    @staticmethod
    def _recv_exact(sock, size):
        data = bytearray()
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                raise ModbusError("Verbindung geschlossen")
            data.extend(chunk)
        return bytes(data)

    def read_coils(self, address, count=1):
        body = self._request(struct.pack(">BHH", 1, int(address), int(count)))
        byte_count = body[1]
        data = body[2:2 + byte_count]
        bits = []
        for byte in data:
            for bit in range(8):
                bits.append(bool(byte & (1 << bit)))
        return bits[:count]

    def read_holding_registers(self, address, count=1):
        body = self._request(struct.pack(">BHH", 3, int(address), int(count)))
        byte_count = body[1]
        values = struct.unpack(f">{byte_count // 2}H", body[2:2 + byte_count])
        return list(values)

    def write_register(self, address, value):
        self._request(struct.pack(">BHH", 6, int(address), int(value) & 0xFFFF))
        return True

    def write_registers(self, address, values):
        payload = b"".join(struct.pack(">H", int(value) & 0xFFFF)
                           for value in values)
        self._request(struct.pack(">BHHB", 16, int(address), len(values),
                                  len(payload)) + payload)
        return True
