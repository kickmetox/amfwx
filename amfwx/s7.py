"""Experimental S7comm client for Siemens S7 PLCs.

The protocol is implemented at packet level. It is not certified against
all PLC families; test against the target CPU before production use.
"""

from __future__ import annotations

import socket
import struct


AREA_DB = 0x84
AREA_MERKER = 0x83
AREA_INPUT = 0x81
AREA_OUTPUT = 0x82

COTP_CR = bytes.fromhex("0300001611e00000000100c1020100c2020102c0010a")


class S7Error(RuntimeError):
    pass


def _tpkt(payload):
    return struct.pack(">BBH", 3, 0, len(payload) + 4) + payload


def _cotp_dt(payload):
    return bytes([0x02, 0xF0, 0x80]) + payload


def _s7_header(pdu_ref, param_length, data_length=0):
    return struct.pack(">BBHHHH", 0x32, 0x01, 0, pdu_ref,
                       param_length, data_length)


def build_setup(pdu_ref=1):
    params = struct.pack(">BBHHH", 0xF0, 0, 1, 1, 0x03C0)
    return _tpkt(_cotp_dt(_s7_header(pdu_ref, len(params)) + params))


def build_read(area, db, start, size, pdu_ref=1):
    params = struct.pack(">BB", 0x04, 1)
    params += bytes([0x12, 0x0A, 0x10, 0x02])
    params += struct.pack(">H", int(size))
    params += struct.pack(">H", int(db))
    params += bytes([int(area)])
    params += int(start * 8).to_bytes(3, "big")
    return _tpkt(_cotp_dt(_s7_header(pdu_ref, len(params)) + params))


def build_write(area, db, start, data, pdu_ref=1):
    payload = bytes(data)
    params = struct.pack(">BB", 0x05, 1)
    params += bytes([0x12, 0x0A, 0x10, 0x02])
    params += struct.pack(">H", len(payload))
    params += struct.pack(">H", int(db))
    params += bytes([int(area)])
    params += int(start * 8).to_bytes(3, "big")
    data_part = bytes([0x00, 0x04]) + struct.pack(">H", len(payload) * 8)
    data_part += payload
    return _tpkt(_cotp_dt(_s7_header(pdu_ref, len(params), len(data_part)) +
                          params + data_part))


def _recv_exact(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise S7Error("Verbindung geschlossen")
        data.extend(chunk)
    return bytes(data)


def _recv_tpkt(sock):
    header = _recv_exact(sock, 4)
    if header[0] != 3:
        raise S7Error("kein TPKT")
    length = struct.unpack(">H", header[2:4])[0]
    return _recv_exact(sock, length - 4)


def _parse_s7(data):
    if len(data) < 10 or data[0] != 0x32:
        raise S7Error("kein S7-Header")
    param_length, data_length = struct.unpack(">HH", data[6:10])
    params = data[10:10 + param_length]
    payload = data[10 + param_length:10 + param_length + data_length]
    return params, payload


class S7Client:
    def __init__(self, host, port=102, timeout=3.0):
        self.host = str(host)
        self.port = int(port)
        self.timeout = float(timeout)
        self.socket = None
        self.pdu_ref = 0

    def connect(self):
        self.socket = socket.create_connection((self.host, self.port),
                                               timeout=self.timeout)
        self.socket.sendall(COTP_CR)
        _recv_tpkt(self.socket)
        self.socket.sendall(build_setup(self._next_ref()))
        _recv_tpkt(self.socket)
        return self

    def _next_ref(self):
        self.pdu_ref = (self.pdu_ref + 1) & 0xFFFF
        return self.pdu_ref

    def _require(self):
        if self.socket is None:
            raise S7Error("nicht verbunden")

    def _request(self, packet):
        self._require()
        self.socket.sendall(packet)
        return _parse_s7(_recv_tpkt(self.socket))

    def read_area(self, area, db, start, size):
        _params, data = self._request(build_read(area, db, start, size,
                                                 self._next_ref()))
        if len(data) < 4 or data[0] != 0xFF:
            raise S7Error("S7-Lesefehler")
        length = struct.unpack(">H", data[2:4])[0] // 8
        return data[4:4 + max(0, length)]

    def read_db(self, db, start, size):
        return self.read_area(AREA_DB, db, start, size)

    def write_area(self, area, db, start, data):
        _params, payload = self._request(
            build_write(area, db, start, data, self._next_ref()))
        if len(payload) < 1 or payload[0] != 0xFF:
            raise S7Error("S7-Schreibfehler")
        return True

    def write_db(self, db, start, data):
        return self.write_area(AREA_DB, db, start, data)

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
