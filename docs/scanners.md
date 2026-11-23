# Scanners: WIA and TWAIN

## WIA

Optional COM automation via `comtypes`:

```powershell
pip install comtypes
```

```python
from amfwx import list_wia_devices

for device in list_wia_devices():
    print(device.name, device.device_id)
```

WIA is the modern Windows scanner API. It works for 32-bit and 64-bit
applications through COM registration.

If `comtypes` is missing or no WIA service is available, the list is empty.

## TWAIN

```python
from amfwx import list_twain_sources

for source in list_twain_sources():
    print(source.product_name, source.manufacturer)
```

The loader tries:

1. bundled `amfwx/bin/TWAINDSM.dll` / `TWAINDSM32.dll`
2. system `twaindsm.dll`
3. legacy `twain_32.dll` (only 32-bit Python)

The official TWAIN DSM 2.5.1 binaries are bundled:

- `TWAINDSM.dll` (64-bit)
- `TWAINDSM32.dll` (32-bit)
- `LICENSE-TWAINDSM.txt` (LGPL v2+)

Both were signed by the TWAIN Working Group. Source:
<https://github.com/twain/twain-dsm>

## 32-bit bridge

32-bit-only drivers (for example Canon `CISDS.DS`) are used through a
32-bit helper process:

```python
from amfwx import list_twain32_sources, scan_twain32

for source in list_twain32_sources():
    print(source.name, source.manufacturer)

scan_twain32("CanoScan LiDE 210", "scan.bmp")
```

The helper needs a 32-bit Python. Set `AMFWX_PYTHON32` or place it at
`vendor/python32/python.exe`.

## 32/64-bit

| Python | WIA | TWAIN |
|---|---|---|
| 32-bit | COM | `twain_32.dll` or DSM |
| 64-bit | COM | 64-bit `twaindsm.dll` |

`twain_32.dll` cannot be loaded into a 64-bit process. That is a Windows
architecture rule, not an AMFWX limitation.

## WIA acquisition

```python
from amfwx import WiaScanner

WiaScanner(index=1).acquire("scan.png", dpi=300, color=1)
WiaScanner(index=1).acquire_pages("out", prefix="page")
```

ADF/duplex depends on the scanner driver exposing multiple WIA items.
Flatbed drivers usually report one item.

## Not implemented

- TWAIN image acquisition
- TWAIN memory/file transfer
- WIA item transfer
- ADF/duplex settings
- resolution/color settings
- scanner UI

Enumeration is implemented; actual scanning is the next step.

## Limits

- optional `comtypes` for WIA
- vendor DSM required for TWAIN 64-bit
- no hardware-in-the-loop CI

## Scan to folder

```powershell
python -m amfwx --scan-host 192.168.178.93 --scan-source Platen --scan-pages 1 --scan-dir "D:\Scans"
```

The CLI writes directly into the destination folder. Feeder scans request paper in the ADF; an empty feeder is reported clearly.

## Scan as PDF

```powershell
python -m amfwx --scan-host 192.168.178.93 --scan-source Platen --scan-pdf "D:\Scans\scan.pdf"
```

Echter Kyocera-Test: PDF 1.4, 435967 Bytes.
