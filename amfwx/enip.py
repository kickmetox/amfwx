"""EtherNet/IP ListIdentity discovery."""

from __future__ import annotations

import socket
import struct


ENIP_PORT = 44818
LIST_IDENTITY = 0x0063
ITEM_LIST_IDENTITY = 0x000C


class EnipError(RuntimeError):
    pass


class EnipDevice:
    def __init__(self, host, port, vendor_id, device_type, product_code,
                 revision, status, serial, product_name, state):
        self.host = host
        self.port = int(port)
        self.vendor_id = int(vendor_id)
        self.device_type = int(device_type)
        self.product_code = int(product_code)
        self.revision = int(revision)
        self.status = int(status)
        self.serial = int(serial)
        self.product_name = product_name
        self.state = int(state)

    def __repr__(self):
        return (f"EnipDevice({self.product_name!r}, {self.host}:{self.port}, "
                f"vendor={self.vendor_id})")


def build_request():
    return struct.pack("<HHII8sI", LIST_IDENTITY, 0, 0, 0, b"\x00" * 8, 0)


def _parse_socket_address(data, offset):
    family, port = struct.unpack(">HH", data[offset:offset + 4])
    address = ".".join(str(byte) for byte in data[offset + 4:offset + 8])
    return family, port, address, offset + 16


def parse_response(data, host=""):
    if len(data) < 24:
        raise EnipError("Antwort zu kurz")
    command, length, _session, _status, _context, _options = struct.unpack(
        "<HHII8sI", data[:24])
    if command != LIST_IDENTITY:
        raise EnipError(f"falscher Command: {command:#x}")
    payload = data[24:24 + length]
    if len(payload) < 2:
        raise EnipError("kein Item")
    count = struct.unpack("<H", payload[:2])[0]
    offset = 2
    devices = []
    for _ in range(count):
        if offset + 4 > len(payload):
            break
        item_type, item_length = struct.unpack("<HH",
                                               payload[offset:offset + 4])
        offset += 4
        item = payload[offset:offset + item_length]
        offset += item_length
        if item_type != ITEM_LIST_IDENTITY or len(item) < 24:
            continue
        _version = struct.unpack("<H", item[:2])[0]
        _family, port, address, position = _parse_socket_address(item, 2)
        vendor, device_type, product_code, revision, status, serial = (
            struct.unpack("<HHHHHI", item[position:position + 14]))
        position += 14
        name_length = item[position]
        position += 1
        name = item[position:position + name_length].decode("utf-8",
                                                             "replace")
        position += name_length
        state = item[position] if position < len(item) else 0
        devices.append(EnipDevice(address or host, port, vendor, device_type,
                                  product_code, revision, status, serial,
                                  name, state))
    return devices


def list_identity(host, timeout=2.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(float(timeout))
    try:
        sock.sendto(build_request(), (str(host), ENIP_PORT))
        data, address = sock.recvfrom(2048)
    except socket.timeout as error:
        raise EnipError(f"keine Antwort von {host}") from error
    finally:
        sock.close()
    return parse_response(data, address[0])


def discover(timeout=2.0, broadcast="255.255.255.255"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(float(timeout))
    devices = []
    try:
        sock.sendto(build_request(), (str(broadcast), ENIP_PORT))
        while True:
            try:
                data, address = sock.recvfrom(2048)
            except socket.timeout:
                break
            try:
                devices.extend(parse_response(data, address[0]))
            except EnipError:
                continue
    finally:
        sock.close()
    return devices
