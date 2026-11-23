# AMFWX 3.95.1

Reject non-eSCL HTTP responses.

## Fix

- `probe_escl` now requires `ScannerCapabilities` in the body
- prevents routers/repeaters from being reported as scanners
- 351 tests

## Real result

Subnet scan found a TP-Link repeater at `192.168.178.144:80`; it was a false
positive and is now reported as `escl=False`.
