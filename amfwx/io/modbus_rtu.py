"""Modbus RTU client over a serial transport."""

from __future__ import annotations

import struct

from .serial import SerialPort


class ModbusRTUError(RuntimeError):
    pass


def crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


class ModbusRTU:
    def __init__(self, port=None, baudrate=9600, unit=1, timeout=1.0,
                 transport=None):
        self.unit = int(unit)
        self.timeout = float(timeout)
        self.transport = transport
        self.port = None
        if transport is None:
            if port is None:
                raise ValueError("port oder transport erforderlich")
            self.port = SerialPort(port, baudrate, timeout)

    def open(self):
        if self.port is not None:
            self.port.open()
        return self

    def close(self):
        if self.port is not None:
            self.port.close()
        return self

    def _read(self, size):
        data = bytearray()
        while len(data) < size:
            chunk = self.transport.read(size - len(data))
            if not chunk:
                raise ModbusRTUError("Timeout/keine Antwort")
            data.extend(chunk)
        return bytes(data)

    def _write(self, data):
        self.transport.write(data)

    def _request(self, pdu):
        frame = bytes([self.unit]) + pdu
        frame += struct.pack("<H", crc16(frame))
        self._write(frame)
        head = self._read(2)
        unit, function = head
        if unit != self.unit:
            raise ModbusRTUError(f"falsche Unit: {unit}")
        if function & 0x80:
            rest = self._read(3)
            raise ModbusRTUError(f"Modbus-Exception {rest[0]}")
        if function in (1, 2, 3, 4):
            byte_count = self._read(1)[0]
            data = self._read(byte_count)
            crc = self._read(2)
            if struct.unpack("<H", crc)[0] != crc16(head + bytes([byte_count]) + data):
                raise ModbusRTUError("CRC falsch")
            return bytes([function, byte_count]) + data
        rest = self._read(6)
        crc = rest[-2:]
        if struct.unpack("<H", crc)[0] != crc16(head + rest[:-2]):
            raise ModbusRTUError("CRC falsch")
        return head + rest[:-2]

    def read_coils(self, address, count=1):
        body = self._request(struct.pack(">BHH", 1, int(address), int(count)))
        bits = []
        for byte in body[2:]:
            for bit in range(8):
                bits.append(bool(byte & (1 << bit)))
        return bits[:count]

    def read_holding_registers(self, address, count=1):
        body = self._request(struct.pack(">BHH", 3, int(address), int(count)))
        return list(struct.unpack(f">{len(body[2:]) // 2}H", body[2:]))

    def write_register(self, address, value):
        self._request(struct.pack(">BHH", 6, int(address), int(value) & 0xFFFF))
        return True

    def write_registers(self, address, values):
        payload = b"".join(struct.pack(">H", int(value) & 0xFFFF)
                           for value in values)
        self._request(struct.pack(">BHHB", 16, int(address), len(values),
                                  len(payload)) + payload)
        return True

    def __enter__(self):
        return self.open()

    def __exit__(self, *_exc):
        self.close()
