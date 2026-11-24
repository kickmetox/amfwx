"""Becker Centronic USB serial stick (868 MHz)."""

from __future__ import annotations

import re
import shutil

try:
    import serial
    import serial.tools.list_ports
except ImportError:  # optional
    serial = None

STX = b"\x02"
ETX = b"\x03"
PREFIX = "0000000002010B"
SUFFIX = "000000"
CODE_21 = "021"
REMOTE_TYPE = "01"

COMMANDS = {
    "release": 0x00,
    "stop": 0x10,
    "up": 0x20,
    "up_intermediate": 0x24,
    "down": 0x40,
    "down_intermediate": 0x44,
    "pair": 0x80,
}


class BeckerError(RuntimeError):
    pass


def hex2(value):
    return f"{value & 0xFF:02X}"


def hex4(value):
    return f"{value & 0xFFFF:04X}"


def checksum(code):
    if len(code) != 40:
        raise BeckerError("Becker-Code muss 40 Zeichen haben")
    total = sum(int(code[index:index + 2], 16)
                for index in range(0, 40, 2))
    return code.upper() + hex2(0x03 - total)


def generate_code(channel, unit_id, increment, command,
                  remote_type=REMOTE_TYPE):
    channel = int(channel)
    if not 1 <= channel <= 7 and channel != 15:
        raise BeckerError("Kanal muss 1-7 oder 15 sein")
    unit_id = str(unit_id).upper()
    if not re.fullmatch(r"[0-9A-F]{5}", unit_id):
        raise BeckerError("Unit-ID muss 5 Hex-Zeichen haben")
    code = (PREFIX + hex4(int(increment)) + SUFFIX + unit_id + CODE_21 +
            remote_type + hex2(channel) + "00" + hex2(int(command)))
    return checksum(code)


def finalize(code):
    return STX + code.encode("ascii") + ETX


COMMAND_NAMES = {
    0x00: "release", 0x10: "stop", 0x20: "up", 0x24: "up_intermediate",
    0x40: "down", 0x44: "down_intermediate", 0x80: "pair",
}


def parse_packet(data):
    data = bytes(data)
    start = data.find(STX)
    end = data.find(ETX, start + 1)
    if start < 0 or end < 0:
        raise BeckerError("kein Becker-Rahmen")
    code = data[start + 1:end].decode("ascii", "replace").strip()
    if len(code) != 42:
        raise BeckerError(f"Becker-Code ungueltig: {len(code)} Zeichen")
    body, check = code[:40].upper(), code[40:].upper()
    if checksum(body)[40:] != check:
        raise BeckerError("Becker-Checksumme ungueltig")
    return {
        "unit": body[24:29],
        "channel": int(body[34:36], 16),
        "command_code": int(body[38:40], 16),
        "command": COMMAND_NAMES.get(int(body[38:40], 16), "unknown"),
        "increment": int(body[14:18], 16),
        "code": code,
    }


def available():
    return serial is not None


def list_sticks():
    if serial is None:
        return []
    found = []
    for port in serial.tools.list_ports.comports():
        text = f"{port.device} {port.description} {port.manufacturer or ''}"
        if "becker" in text.lower():
            found.append({"device": port.device,
                          "description": port.description})
    return found


class BeckerStick:
    def __init__(self, port, unit_id="1737B", increment=0, timeout=1.0,
                 serial_factory=None):
        if serial is None and serial_factory is None:
            raise BeckerError("pyserial fehlt: pip install pyserial")
        self.port = str(port)
        self.unit_id = str(unit_id).upper()
        self.increment = int(increment)
        self.timeout = float(timeout)
        self.factory = serial_factory or serial.Serial
        self.connection = self.factory(self.port, 115200, timeout=self.timeout)

    def send_code(self, code):
        self.connection.write(finalize(code))
        self.increment += 1
        return code

    def command(self, channel, name):
        if name not in COMMANDS:
            raise BeckerError(f"unbekannter Befehl: {name}")
        code = generate_code(channel, self.unit_id, self.increment,
                             COMMANDS[name])
        return self.send_code(code)

    def up(self, channel):
        return self.command(channel, "up")

    def down(self, channel):
        return self.command(channel, "down")

    def stop(self, channel):
        return self.command(channel, "stop")

    def pair(self, channel):
        return self.command(channel, "pair")

    def read_packet(self, size=256):
        data = self.connection.read(size)
        if not data:
            return None
        return parse_packet(data)

    def listen(self, callback, duration=10.0):
        import time
        deadline = time.monotonic() + float(duration)
        packets = []
        while time.monotonic() < deadline:
            packet = self.read_packet()
            if packet is not None:
                packets.append(packet)
                callback(packet)
        return packets

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
