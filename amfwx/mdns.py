"""Minimal mDNS/DNS-SD discovery (Bonjour-style)."""

from __future__ import annotations

import socket
import struct
import time


MDNS_ADDRESS = "224.0.0.251"
MDNS_PORT = 5353
TYPE_A = 1
TYPE_PTR = 12
TYPE_TXT = 16
TYPE_AAAA = 28
TYPE_SRV = 33
CLASS_IN = 1


class DnsError(ValueError):
    pass


def encode_name(name):
    output = bytearray()
    for label in str(name).rstrip(".").split("."):
        if not label:
            continue
        data = label.encode("utf-8")
        if len(data) > 63:
            raise DnsError("Label zu lang")
        output.append(len(data))
        output.extend(data)
    output.append(0)
    return bytes(output)


def decode_name(data, offset):
    labels = []
    jumped = False
    end = offset
    while True:
        if offset >= len(data):
            raise DnsError("Name abgeschnitten")
        length = data[offset]
        if length == 0:
            offset += 1
            if not jumped:
                end = offset
            break
        if length & 0xC0 == 0xC0:
            if offset + 1 >= len(data):
                raise DnsError("Zeiger abgeschnitten")
            pointer = ((length & 0x3F) << 8) | data[offset + 1]
            if not jumped:
                end = offset + 2
            offset = pointer
            jumped = True
            continue
        offset += 1
        labels.append(data[offset:offset + length].decode("utf-8", "replace"))
        offset += length
    return ".".join(labels), end


def build_query(name, qtype=TYPE_PTR, qclass=CLASS_IN):
    header = struct.pack(">HHHHHH", 0, 0, 1, 0, 0, 0)
    return header + encode_name(name) + struct.pack(">HH", qtype, qclass)


def parse_packet(data):
    if len(data) < 12:
        raise DnsError("Paket zu kurz")
    _id, _flags, questions, answers, authority, additional = struct.unpack(
        ">HHHHHH", data[:12])
    offset = 12
    for _ in range(questions):
        _name, offset = decode_name(data, offset)
        offset += 4
    records = []
    for _ in range(answers + authority + additional):
        name, offset = decode_name(data, offset)
        if offset + 10 > len(data):
            break
        rtype, rclass, _ttl, length = struct.unpack(">HHIH",
                                                   data[offset:offset + 10])
        offset += 10
        rdata = data[offset:offset + length]
        offset += length
        value = None
        if rtype == TYPE_PTR:
            value, _ = decode_name(data, offset - length)
        elif rtype == TYPE_SRV and len(rdata) >= 7:
            _priority, _weight, port = struct.unpack(">HHH", rdata[:6])
            target, _ = decode_name(data, offset - length + 6)
            value = {"port": port, "target": target}
        elif rtype == TYPE_TXT:
            value = rdata
        elif rtype == TYPE_A and len(rdata) == 4:
            value = ".".join(str(byte) for byte in rdata)
        elif rtype == TYPE_AAAA and len(rdata) == 16:
            value = ":".join(f"{rdata[i]:02x}{rdata[i + 1]:02x}"
                             for i in range(0, 16, 2))
        records.append({"name": name, "type": rtype, "class": rclass,
                        "value": value})
    return records


class Service:
    def __init__(self, service_type, name="", host="", port=0):
        self.service_type = service_type
        self.name = name
        self.host = host
        self.port = int(port)

    def __repr__(self):
        return (f"Service({self.service_type!r}, {self.name!r}, "
                f"{self.host}:{self.port})")


def discover(service_type="_http._tcp.local", timeout=2.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(max(0.1, float(timeout)))
    services = []
    try:
        sock.sendto(build_query(service_type), (MDNS_ADDRESS, MDNS_PORT))
        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            try:
                data, _address = sock.recvfrom(9000)
            except socket.timeout:
                break
            try:
                records = parse_packet(data)
            except DnsError:
                continue
            ptr_targets = [record["value"] for record in records
                           if record["type"] == TYPE_PTR and
                           record["name"].lower() == service_type.lower()]
            for target in ptr_targets:
                port = 0
                host = ""
                for record in records:
                    if record["name"] == target and record["type"] == TYPE_SRV:
                        port = record["value"]["port"]
                        host = record["value"]["target"]
                services.append(Service(service_type, target, host, port))
    finally:
        sock.close()
    return services
