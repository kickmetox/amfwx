# AMFWX 5.10.0

Unified scanner CLI.

## New

- `--list-scanners`
- `--scan-wia ID`
- `--scan-twain32 SOURCE`
- `--scan-naps2 SOURCE`
- `--scan-dpi`
- `--scan-adf`
- PDF output through `--scan-pdf`
- 385 tests

## Real 32-bit scan

```text
CanoScan LiDE 210
TWAIN 32-bit
PDF: 1,527,665 bytes
```

The Canon scan ran through `vendor/python32` and produced a valid PDF.

## Listing

```text
WIA:      Kyocera, CanoScan
TWAIN:    VueScan TWAIN
TWAIN32:  CanoScan LiDE 210, Kyocera, WIA variants
NAPS2:    empty (not installed)
```

## Commands

```powershell
python -m amfwx --list-scanners
python -m amfwx --scan-twain32 "CanoScan LiDE 210" --scan-pdf "scan.pdf"
python -m amfwx --scan-wia "{...}" --scan-pdf "scan.pdf"
```
