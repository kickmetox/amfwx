# Network printers and scanners

```python
from amfwx import discover_network_devices, probe_escl

for device in discover_network_devices(timeout=4.0):
    print(device.kind, device.name, device.address, device.port)

if probe_escl("192.168.1.50"):
    print("eSCL scanner")
```

## Service types

- `_ipp._tcp`
- `_ipps._tcp`
- `_printer._tcp`
- `_pdl-datastream._tcp`
- `_scanner._tcp`
- `_uscan._tcp`
- `_uscans._tcp`

`NetworkDevice.kind` is `scanner`, `printer` or `device`.

## Backends

1. Optional `zeroconf` package (best results)
2. Built-in mDNS fallback

```powershell
pip install zeroconf
```

## eSCL

`probe_escl()` checks:

```text
http://host:port/eSCL/ScannerCapabilities
```

This detects AirScan/eSCL scanners, including many Canon, HP, Brother and
Epson network devices. Actual eSCL scanning is not implemented yet.

## Limits

- no IPP print job submission
- no eSCL scan job yet
- no WSD discovery
- multicast/firewall dependent
