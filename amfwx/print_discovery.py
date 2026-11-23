"""Explicit LAN scan for eSCL/IPP printer endpoints."""

from __future__ import annotations

import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor

from .network_scan import probe_escl


class PrinterEndpoint:
    def __init__(self, host, port, escl=False):
        self.host = host
        self.port = int(port)
        self.escl = bool(escl)

    def __repr__(self):
        return f"PrinterEndpoint({self.host!r}, {self.port}, escl={self.escl})"


def scan_host(host, ports=(80, 631), timeout=0.25):
    found = []
    for port in ports:
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                pass
        except OSError:
            continue
        found.append(PrinterEndpoint(host, port,
                                     probe_escl(host, port, timeout=timeout)))
    return found


def scan_network(cidr, ports=(80, 631), timeout=0.25, workers=64):
    network = ipaddress.ip_network(str(cidr), strict=False)
    hosts = list(network.hosts()) if network.num_addresses > 1 else [network.network_address]
    endpoints = []
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        futures = [pool.submit(scan_host, str(host), ports, timeout)
                   for host in hosts]
        for future in futures:
            try:
                endpoints.extend(future.result())
            except Exception:
                pass
    return sorted(endpoints, key=lambda item: (item.host, item.port))
