# AMFWX 3.95.0

Explicit eSCL/IPP subnet scan.

## New

- `scan_network`
- `PrinterEndpoint`
- `--scan-printers CIDR`
- eSCL probe per open port
- 350 tests

## Usage

```powershell
python -m amfwx --scan-printers 192.168.178.0/24
```

## Note

Only runs when explicitly requested; normal discovery stays passive.
