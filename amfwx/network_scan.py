"""Network printer/scanner discovery (Bonjour/mDNS + eSCL probe)."""

from __future__ import annotations

from .mdns import discover as discover_mdns
from .net import HttpClient, NetworkError


SERVICE_TYPES = (
    "_ipp._tcp.local.",
    "_ipps._tcp.local.",
    "_printer._tcp.local.",
    "_pdl-datastream._tcp.local.",
    "_scanner._tcp.local.",
    "_uscan._tcp.local.",
    "_uscans._tcp.local.",
    "_kizboxdev._tcp.local.",
    "_matter._tcp.local.",
    "_matterc._udp.local.",
)


class NetworkDevice:
    def __init__(self, name, service_type, host="", address="", port=0):
        self.name = name
        self.service_type = service_type
        self.host = host
        self.address = address
        self.port = int(port) if port else 0

    @property
    def kind(self):
        value = self.service_type.lower()
        if "kizboxdev" in value:
            return "tahoma"
        if "matter" in value:
            return "matter"
        if "uscan" in value or "scanner" in value or "escl" in value:
            return "scanner"
        if "ipp" in value or "printer" in value or "pdl-datastream" in value:
            return "printer"
        return "device"

    def __repr__(self):
        return (f"NetworkDevice({self.name!r}, {self.service_type!r}, "
                f"{self.address}:{self.port})")


def discover_zeroconf(timeout=4.0):
    try:
        from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
    except ImportError:
        return []
    found = []

    class Listener(ServiceListener):
        def add_service(self, zc, service_type, name):
            info = zc.get_service_info(service_type, name)
            if info:
                found.append((service_type, info))

        def update_service(self, zc, service_type, name):
            pass

        def remove_service(self, zc, service_type, name):
            pass

    zc = Zeroconf()
    browsers = []
    try:
        for service_type in SERVICE_TYPES:
            browsers.append(ServiceBrowser(zc, service_type, Listener()))
        import time
        time.sleep(float(timeout))
    finally:
        for browser in browsers:
            try:
                browser.cancel()
            except Exception:
                pass
        zc.close()
    devices = []
    for service_type, info in found:
        addresses = info.parsed_addresses() if hasattr(info, "parsed_addresses") else []
        address = addresses[0] if addresses else ""
        host = (info.server or "").rstrip(".") or address
        name = info.name.split(".")[0] if info.name else host
        devices.append(NetworkDevice(name, service_type.rstrip("."), host,
                                     address, info.port or 0))
    return _unique(devices)


def discover_network_devices(timeout=4.0):
    devices = discover_zeroconf(timeout)
    if devices:
        return devices
    for service_type in SERVICE_TYPES:
        try:
            services = discover_mdns(service_type, timeout=min(1.0, float(timeout)))
        except Exception:
            continue
        for service in services:
            devices.append(NetworkDevice(service.name, service_type,
                                         service.host, service.host,
                                         service.port))
    return _unique(devices)


def _unique(devices):
    seen = set()
    result = []
    for device in devices:
        key = (device.name, device.service_type, device.address)
        if key not in seen:
            seen.add(key)
            result.append(device)
    return result


def probe_escl(host, port=80, timeout=3.0):
    """Return True if the endpoint exposes eSCL scanner capabilities."""
    try:
        client = HttpClient(f"http://{host}:{int(port)}", timeout=timeout)
        response = client.request("/eSCL/ScannerCapabilities")
    except (NetworkError, OSError, ValueError):
        return False
    return response["status"] == 200
