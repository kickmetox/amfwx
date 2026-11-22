# AMFWX 3.47.0

AMFWX 3.47 adds network printer/scanner discovery.

## New

- `discover_network_devices`
- mDNS service types for IPP, IPPS, printer, PDL, scanner, eSCL
- optional `zeroconf` backend
- built-in mDNS fallback
- `probe_escl`
- `NetworkDevice.kind`
- 266 tests

## Notes

- no IPP print job
- no eSCL scan job yet
- no WSD discovery
- multicast/firewall dependent
- Windows-only
- unsigned installer
