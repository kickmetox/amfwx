"""Home-network discovery and HTTP fingerprinting."""

from __future__ import annotations

import json
import socket
import time
import xml.etree.ElementTree as ET

from .net import HttpClient, NetworkError


SSDP_ADDRESS = ("239.255.255.250", 1900)
KNX_ADDRESS = ("224.0.23.12", 3671)
KNX_SEARCH = bytes.fromhex("06100205000A00000000")

SSDP_MESSAGE = ("M-SEARCH * HTTP/1.1\r\n"
                "HOST: 239.255.255.250:1900\r\n"
                'MAN: "ssdp:discover"\r\n'
                "MX: 2\r\n"
                "ST: ssdp:all\r\n\r\n")


class DiscoveredDevice:
    def __init__(self, kind, name, host, port=80, source="", evidence=""):
        self.kind = kind
        self.name = name
        self.host = host
        self.port = int(port)
        self.source = source
        self.evidence = evidence

    def __repr__(self):
        return (f"DiscoveredDevice({self.kind!r}, {self.name!r}, "
                f"{self.host}:{self.port})")


def parse_ssdp(data, address=""):
    text = data.decode("utf-8", "replace")
    lines = text.splitlines()
    if not lines or "200" not in lines[0]:
        return None
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    location = headers.get("location", "")
    host = address
    if location:
        from urllib.parse import urlparse
        host = urlparse(location).hostname or host
    return {"host": host, "location": location, "server": headers.get("server", ""),
            "st": headers.get("st", ""), "headers": headers}


def ssdp_discover(timeout=2.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(0.3)
    found = []
    try:
        sock.sendto(SSDP_MESSAGE.encode(), SSDP_ADDRESS)
        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            try:
                data, address = sock.recvfrom(65535)
            except socket.timeout:
                continue
            parsed = parse_ssdp(data, address[0])
            if parsed:
                found.append(parsed)
    finally:
        sock.close()
    return found


def _xml_text(xml, names):
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return ""
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] in names and element.text:
            return element.text.strip()
    return ""


def probe_http(host, port=80, timeout=1.0):
    client = HttpClient(f"http://{host}:{int(port)}", timeout=timeout)
    checks = [
        ("/shelly", "shelly", ("type", "mac")),
        ("/api/devices", "fibaro", None),
        ("/cm?cmnd=Status%200", "tasmota", ("Status",)),
        ("/api.cgi?cmd=GetDevInfo", "reolink", ("value",)),
        ("/api/v1/devices", "homepilot", None),
        ("/api/setup/devices", "tahoma", None),
    ]
    for path, kind, keys in checks:
        try:
            response = client.request(path)
        except (NetworkError, OSError):
            continue
        if response["status"] != 200:
            continue
        body = response["body"]
        try:
            data = json.loads(body.decode("utf-8", "replace"))
        except ValueError:
            data = None
        name = kind
        if isinstance(data, dict):
            if keys and not any(key in data for key in keys):
                continue
            name = str(data.get("name") or data.get("type") or
                       data.get("model") or kind)
        elif isinstance(data, list):
            name = kind
            if not data:
                continue
        else:
            continue
        return DiscoveredDevice(kind, name, host, port, "http", path)
    return None


def knx_search(timeout=1.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.3)
    found = []
    try:
        sock.sendto(KNX_SEARCH, KNX_ADDRESS)
        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            try:
                data, address = sock.recvfrom(1024)
            except socket.timeout:
                continue
            if len(data) >= 6 and data[:2] == b"\x06\x10":
                found.append(DiscoveredDevice("knx", "KNX-Gateway",
                                              address[0], 3671, "knx",
                                              data[:2].hex()))
    finally:
        sock.close()
    return found


def tuya_broadcast(timeout=1.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.3)
    found = []
    try:
        sock.sendto(b"\x00" * 16, ("255.255.255.255", 6667))
        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            try:
                data, address = sock.recvfrom(2048)
            except socket.timeout:
                continue
            name = "Tuya-Gerat"
            if data.startswith(b"{"):
                try:
                    name = json.loads(data.decode("utf-8", "replace")).get(
                        "gwId", name)
                except ValueError:
                    pass
            found.append(DiscoveredDevice("tuya", name, address[0], 6667,
                                          "tuya-broadcast",
                                          "encrypted" if not data.startswith(b"{")
                                          else "json"))
    finally:
        sock.close()
    return found


def discover_home(timeout=3.0, fritz=None):
    from .network_scan import discover_network_devices
    devices = []
    for network in discover_network_devices(timeout=min(2.0, timeout)):
        devices.append(DiscoveredDevice(network.kind, network.name,
                                        network.address, network.port or 80,
                                        "mdns", network.service_type))
    for entry in ssdp_discover(timeout=min(2.0, timeout)):
        devices.append(DiscoveredDevice("ssdp", entry["server"] or entry["host"],
                                        entry["host"], 80, "ssdp",
                                        entry["st"]))
    if timeout >= 0.5:
        devices.extend(knx_search(min(1.0, timeout)))
        devices.extend(tuya_broadcast(min(1.0, timeout)))
    hosts = []
    for device in devices:
        if device.host:
            hosts.append((device.host, device.port))
    if fritz is not None:
        try:
            for host in fritz.hosts():
                address = host.get("IPAddress")
                if address:
                    hosts.append((address, 80))
        except Exception:
            pass
    seen = set()
    for host, port in hosts:
        key = (host, port)
        if key in seen:
            continue
        seen.add(key)
        probe = probe_http(host, port, timeout=min(1.0, timeout))
        if probe:
            devices.append(probe)
    unique = []
    known = set()
    for device in devices:
        key = (device.kind, device.host, device.port)
        if key not in known:
            known.add(key)
            unique.append(device)
    return unique
